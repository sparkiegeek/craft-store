# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64
import json
import pathlib
from typing import TYPE_CHECKING, Any, Dict, Optional, TextIO
from urllib.parse import urlparse

import macaroonbakery._utils as utils
import requests
from macaroonbakery import bakery, httpbakery

from . import config, errors, http_client

if TYPE_CHECKING:
    from . import endpoints


class WebBrowserWaitingInteractor(httpbakery.WebBrowserInteractor):
    """WebBrowserInteractor implementation using .http_client.Client.

    Waiting for a token is implemented using _http_client.Client which mounts
    a session with backoff retires.

    Better exception classes and messages are  provided to handle errors.
    """

    def __init__(self, user_agent: str) -> None:
        super().__init__()
        self.user_agent = user_agent

    # TODO: transfer implementation to macaroonbakery.
    def _wait_for_token(self, ctx, wait_token_url):
        request_client = http_client.HTTPClient(user_agent=self.user_agent)
        resp = request_client.request("GET", wait_token_url)
        if resp.status_code != 200:
            raise errors.CandidTokenTimeoutError(url=wait_token_url)
        json_resp = resp.json()
        kind = json_resp.get("kind")
        if kind is None:
            raise errors.CandidTokenKindError(url=wait_token_url)
        token_val = json_resp.get("token")
        if token_val is None:
            token_val = json_resp.get("token64")
            if token_val is None:
                raise errors.CandidTokenValueError(url=wait_token_url)
            token_val = base64.b64decode(token_val)
        return httpbakery._interactor.DischargeToken(kind=kind, value=token_val)


class StoreConfig(config.Config):
    """Hold configuration options in sections.

    There can be two sections for the sso related credentials: production and
    staging. This is governed by the STORE_DASHBOARD_URL environment
    variable. Other sections are ignored but preserved.

    """

    def __init__(self, *, store_base_url: str, config_path: pathlib.Path):
        self.store_base_url = urlparse(store_base_url).netloc
        self.config_path = config_path

        super().__init__()

    def _get_section_name(self) -> str:
        return self.store_base_url

    def _get_config_path(self) -> pathlib.Path:
        return self.config_path


class StoreClient(http_client.HTTPClient):
    @property
    def _auth(self) -> Optional[str]:
        auth = self._conf.get("auth")

        if auth is None:
            raise errors.CredentialsMissingError()

        return auth

    @_auth.setter
    def _auth(self, auth: str) -> None:
        self._conf.set("auth", auth)
        if self._conf_save:
            self._conf.save()

    @property
    def _token_request(self) -> Dict[str, Any]:
        token_request = self._conf.get("token-request")

        if token_request is None:
            raise errors.MissingTokenRequestError()

        return token_request

    @_token_request.setter
    def _token_request(self, token_request: Dict[str, Any]) -> None:
        self._conf.set("token-request", token_request)
        if self._conf_save:
            self._conf.save()

    def __init__(
        self,
        *,
        base_url: str,
        endpoints: "endpoints.Endpoints",
        config_path: pathlib.Path,
        user_agent: str,
    ) -> None:
        super().__init__(user_agent=user_agent)

        self.bakery_client = httpbakery.Client(
            interaction_methods=[WebBrowserWaitingInteractor(user_agent=user_agent)]
        )
        self._base_url = base_url
        self._endpoints = endpoints
        self._conf = StoreConfig(
            store_base_url=base_url,
            config_path=config_path,
        )
        self._conf_save = True

    def _get_token(self) -> str:
        token_response = self.request(
            "POST",
            self._endpoints.tokens,
            auth_header=False,
            json=self._token_request,
        )

        return token_response.json()["macaroon"]

    def _candid_discharge(self, macaroon: str) -> str:
        bakery_macaroon = bakery.Macaroon.from_dict(json.loads(macaroon))
        discharges = bakery.discharge_all(
            bakery_macaroon, self.bakery_client.acquire_discharge
        )

        # serialize macaroons the bakery-way
        discharged_macaroons = (
            "[" + ",".join(map(utils.macaroon_to_json_string, discharges)) + "]"
        )

        return base64.urlsafe_b64encode(utils.to_bytes(discharged_macaroons)).decode(
            "ascii"
        )

    def _authorize_token(self, candid_discharged_macaroon: str) -> str:
        token_exchange_response = self.request(
            "POST",
            self._endpoints.tokens_exchange,
            auth_header=False,
            json={},
            headers={"Macaroons": candid_discharged_macaroon},
        )

        return token_exchange_response.json()["macaroon"]

    def _login(self):
        token = self._get_token()
        candid_discharged_macaroon = self._candid_discharge(token)
        store_authorized_macaroon = self._authorize_token(candid_discharged_macaroon)

        # Save the authorization token.
        self._auth = store_authorized_macaroon

    def login(
        self,
        *,
        token_request: Dict[str, Any],
        config_fd: Optional[TextIO] = None,
        save: bool = True,
    ) -> None:
        self._conf_save = save
        if config_fd is not None:
            self._conf.load(config_fd=config_fd)
            if save:
                self._conf.save()
            return

        # Save requested token data for re-login requests.
        self._token_request = token_request
        self._login()

    def whoami(self) -> Dict[str, Any]:
        return self.request("GET", self._endpoints.whoami).json()

    def request(
        self,
        method: str,
        url_path: str,
        params: Dict[str, str] = None,
        headers: Dict[str, str] = None,
        auth_header=True,
        **kwargs,
    ) -> requests.Response:
        if headers and auth_header:
            headers["Authorization"] = f"Macaroon {self._auth}"
        elif auth_header:
            headers = {"Authorization": f"Macaroon {self._auth}"}
        elif auth_header:
            raise RuntimeError("No auth data available")

        response = super().request(
            method,
            self._base_url + url_path,
            params=params,
            headers=headers,
            **kwargs,
        )
        if not response.ok and response.status_code == 401:
            # Login again with same attenuations.
            self._login()

            response = super().request(
                method,
                self._base_url + url_path,
                params=params,
                headers=headers,
                **kwargs,
            )
        elif not response.ok:
            raise errors.StoreServerError(response)

        return response

    def export_login(self, *, config_fd: TextIO, encode: bool):
        self._conf.save(config_fd=config_fd, encode=encode)

    def logout(self) -> None:
        self._conf.clear()
        self._conf.save()
