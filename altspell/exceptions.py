'''
    Altspell  Flask web app for translating traditional English spelling to an alternative spelling
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
    """Exception for database records that cannot be found."""
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")

class TranslationNotFoundError(NotFoundError):
    """Exception for Translations that cannot be found."""
    entity_name: str = "Translation"

class AltspellingNotFoundError(NotFoundError):
    """Exception for Altspellings that cannot be found."""
    entity_name: str = "Altspelling"

class MissingKeyError(Exception):
    """Exception for missing required JSON request body keys."""
    def __init__(self, key_name: str):
        super().__init__(f"Missing key: {key_name}")

class InvalidTypeError(Exception):
    """Exception for JSON request body keys with incorrect types."""
    def __init__(self, key_name: str, cls: Type):
        super().__init__(f"Key '{key_name}' must be of type '{cls.__name__}'")

class EmptyTranslationError(Exception):
    """Exception for empty text translation strings."""
    def __init__(self):
        super().__init__("Cannot save an empty translation")

class NotImplementedFwdError(NotImplementedError):
    """Exception for attempted unimplemented tradspell -> altspell translations."""
    def __init__(self):
        super().__init__("tradspell -> altspell translation is not implemented for this plugin")

class NotImplementedBwdError(NotImplementedError):
    """Exception for attempted unimplemented altspell -> tradspell translations."""
    def __init__(self):
        super().__init__("altspell -> tradspell translation is not implemented for this plugin")

class PluginUnavailableError(Exception):
    """Exception for attempted translations with unavailable plugins."""
    def __init__(self, plugin: str):
        super().__init__(f"Plugin '{plugin}' is unavailable")
