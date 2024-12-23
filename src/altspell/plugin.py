'''
    Altspell  Flask web app for converting traditional English spelling to
    an alternative spelling
    Copyright (C) 2024  Nicholas Johnson

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

from abc import ABC, abstractmethod


class PluginBase(ABC):
    """
    An interface for converter plugins.

    Methods:
        convert_to_altspell(tradspell_text: str) -> str:
            Thread-safe method for converting from traditional English spelling to alternative
            English spelling.
        convert_to_tradspell(altspell_text: str) -> str:
            Thread-safe method for converting from alternative English spelling to traditional
            English spelling.
    """
    @abstractmethod
    def convert_to_altspell(self, tradspell_text: str) -> str:
        """
        Thread-safe method for converting from traditional English spelling to alternative
        English spelling. All concrete subclasses must implement or raise a NotImplementedError.

        Parameters:
            tradspell_text: (str): Text written in the traditional English spelling.

        Returns:
            str: Text written in the alternative English spelling.
        """

    @abstractmethod
    def convert_to_tradspell(self, altspell_text: str) -> str:
        """
        Thread-safe method for converting from alternative English spelling to traditional
        English spelling. All concrete subclasses must implement or a NotImplementedError.

        Parameters:
            altspell_text: (str): Text written in the alternative English spelling.

        Returns:
            str: Text written in the traditional English spelling.
        """
