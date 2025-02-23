'''
    Altspell  Flask web app for converting traditional English spelling to
    an alternative spelling
    Copyright (C) 2025  Nicholas Johnson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from typing import Type


class NotFoundError(Exception):

    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")

class ConversionNotFoundError(NotFoundError):

    entity_name: str = "Conversion"

class AltspellingNotFoundError(NotFoundError):

    entity_name: str = "Altspelling"

class MissingKeyError(Exception):

    def __init__(self, key_name: str):
        super().__init__(f"Missing key: {key_name}")

class InvalidTypeError(Exception):

    def __init__(self, key_name: str, cls: Type):
        super().__init__(f"Key '{key_name}' must be of type '{cls}'")

class EmptyConversionError(Exception):

    def __init__(self):
        super().__init__("Cannot save an empty conversion")

class NotImplementedFwdError(NotImplementedError):

    def __init__(self):
        super().__init__("tradspell -> altspell conversion is not implemented for this plugin")

class NotImplementedBwdError(NotImplementedError):

    def __init__(self):
        super().__init__("altspell -> tradspell conversion is not implemented for this plugin")

class PluginUnavailableError(Exception):

    def __init__(self, plugin: str):
        super().__init__(f"Plugin '{plugin}' is unavailable")
