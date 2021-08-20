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

"""Endpoint definitions for different services.

.. data:: CHARMHUB

    Charmhub set of supported endpoints.

.. data:: SNAP_STORE

    Snap Store set of supported endpoints.
"""


import dataclasses
from typing import Final


@dataclasses.dataclass(repr=True)
class Endpoints:
    """Endpoints used to make requests to a store.

    :param whoami: path to the whoami API.
    :param tokens: path to the tokens API.
    :param tokens_exchange: path to the tokens_exchange API.
    """

    whoami: str
    tokens: str
    tokens_exchange: str


CHARMHUB: Final = Endpoints(
    whoami="/v1/whoami",
    tokens="/v1/tokens",
    tokens_exchange="/v1/tokens/exchange",
)
SNAP_STORE: Final = Endpoints(
    whoami="/api/v2/tokens/whoami",
    tokens="/api/v2/tokens",
    tokens_exchange="/api/v2/tokens/exchange",
)
