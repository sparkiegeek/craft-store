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

"""Craft Store errors."""

import dataclasses
import logging
from typing import Optional

import requests
import urllib3

logger = logging.getLogger(__name__)


_STORE_STATUS_URL = "https://status.snapcraft.io/"


@dataclasses.dataclass(repr=True)
class StoreClientError(Exception):
    """Unexpected error.

    :param brief: Brief description of error.
    :param details: Detailed information.
    :param resolution: Recommendation, if any.
    """

    brief: str
    details: Optional[str] = None
    resolution: Optional[str] = None

    def __str__(self) -> str:
        components = [self.brief]

        if self.details:
            components.append(self.details)

        if self.resolution:
            components.append(self.resolution)

        return "\n".join(components)


class StoreServerError(StoreClientError):

    fmt = "{what}: {error_text} (code {error_code}).\n{action}"

    def __init__(self, response: requests.Response) -> None:
        brief = (
            "Issue encountered while processing your request: " f"{response.reason}."
        )
        self.response = response

        super().__init__(brief=brief)


class StoreNetworkError(StoreClientError):
    def __init__(self, exception: Exception) -> None:
        try:
            if isinstance(exception.args[0], urllib3.exceptions.MaxRetryError):
                brief = "Maximum retries exceeded trying to reach the store."
            else:
                brief = str(exception)
        except IndexError:
            brief = str(exception)

        super().__init__(brief=brief)


class InvalidLoginConfig(StoreClientError):
    def __init__(self, error) -> None:
        super().__init__(brief=f"Invalid login config: {error}.")


class MissingTokenRequestError(StoreClientError):
    def __init__(self) -> None:
        super().__init__(
            brief=f"Authentication informormation missing.",
            resolution="Re authenticate and try again.",
        )


class CandidTokenTimeoutError(StoreClientError):
    def __init__(self, *, url: str) -> None:
        super().__init__(brief=f"Timed out waiting for token response from {url!r}.")


class CandidTokenKindError(StoreClientError):
    def __init__(self, *, url: str) -> None:
        super().__init__(brief=f"Empty token kind returned from {url!r}.")


class CandidTokenValueError(StoreClientError):
    def __init__(self, *, url: str) -> None:
        super().__init__(brief=f"Empty token value returned from {url!r}.")
