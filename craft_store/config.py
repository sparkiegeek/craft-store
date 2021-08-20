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

import abc
import base64
import io
import json
import os
import pathlib
from typing import Any, Dict, Optional, TextIO

import configparser

from . import errors


def _load_config(config_content: str) -> Dict[str, Any]:
    try:
        data = json.loads(config_content)
    except json.decoder.JSONDecodeError as json_error:
        # The config may be base64-encoded, try decoding it
        try:
            decoded_config_content = base64.b64decode(config_content).decode()
        except base64.binascii.Error:  # type: ignore
            # It wasn't base64, so use the original error
            raise errors.InvalidLoginConfig(json_error)

        try:
            data = json.loads(decoded_config_content)
        except json.decoder.JSONDecodeError as json_error:
            raise errors.InvalidLoginConfig(json_error)

    return data


class Config(abc.ABC):
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.load()

    @abc.abstractmethod
    def _get_section_name(self) -> str:
        """Return section name."""

    @abc.abstractmethod
    def _get_config_path(self) -> pathlib.Path:
        """Return Path to configuration file."""

    def get(
        self, option_name: str, section_name: Optional[str] = None
    ) -> Optional[Any]:
        """Return content of section_name/option_name or None if not found."""
        if section_name is None:
            section_name = self._get_section_name()

        try:
            return self.data[section_name][option_name]
        except KeyError:
            return None

    def set(
        self, option_name: str, value: Any, section_name: Optional[str] = None
    ) -> None:
        """Set value to section_name/option_name."""
        if not section_name:
            section_name = self._get_section_name()

        if section_name not in self.data:
            self.data[section_name] = {}

        self.data[section_name][option_name] = value

    def is_section_empty(self, section_name: Optional[str] = None) -> bool:
        """Check if section_name is empty."""
        if section_name is None:
            section_name = self._get_section_name()

        return section_name in self.data

    def load(self, *, config_fd: TextIO = None) -> None:
        if config_fd is not None:
            config_content = config_fd.read()
        elif self._get_config_path().exists():
            with self._get_config_path().open() as config_file:
                config_content = config_file.read()
        else:
            return

        self.data = _load_config(config_content)

    def save(self, *, config_fd: Optional[TextIO] = None, encode: bool = False) -> None:
        config_content = json.dumps(self.data, indent=4)
        if encode:
            config_content = base64.b64encode(config_content.encode()).decode()

        if config_fd:
            print(config_content, file=config_fd)
        else:
            with self._get_config_path().open("w") as config_file:
                print(config_content, file=config_file)
                config_file.flush()
                os.fsync(config_file.fileno())

    def clear(self, section_name: Optional[str] = None) -> None:
        if section_name is None:
            section_name = self._get_section_name()

        if section_name in self.data:
            self.data.pop(section_name)
