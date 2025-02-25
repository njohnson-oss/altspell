'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
    Copyright (C) 2024-2025  Nicholas Johnson

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
    An interface for spelling system plugins. Concrete subclasses must be named 'Plugin'.

    Methods:
        translate_to_respelling(traditional_text: str) -> str:
            Thread-safe method for translating from traditional English spelling to alternative
            English spelling.
        translate_to_traditional_spelling(respelled_text: str) -> str:
            Thread-safe method for translating from alternative English spelling to traditional
            English spelling.
    """

    @abstractmethod
    def translate_to_respelling(self, traditional_text: str) -> str:
        """
        Thread-safe method for translating from traditional English spelling to alternative
        English spelling. All concrete subclasses must implement or raise a NotImplementedError.

        Args:
            traditional_text (str): Text written in the traditional English spelling.

        Returns:
            str: Text written in the alternative English spelling.
        """

    @abstractmethod
    def translate_to_traditional_spelling(self, respelled_text: str) -> str:
        """
        Thread-safe method for translating from alternative English spelling to traditional
        English spelling. All concrete subclasses must implement or a NotImplementedError.

        Args:
            respelled_text (str): Text written in the alternative English spelling.

        Returns:
            str: Text written in the traditional English spelling.
        """
