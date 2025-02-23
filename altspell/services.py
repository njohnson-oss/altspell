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

import uuid
from typing import List
from flask import current_app
from sqlalchemy.exc import IntegrityError
from .repositories import ConversionRepository, AltspellingRepository
from .model import Altspelling, Conversion
from .exceptions import (
    MissingKeyError, InvalidTypeError, EmptyConversionError, PluginUnavailableError
)


class PluginService:
    """A service providing functionality for plugin endpoints."""

    @staticmethod
    def get_plugins() -> List[str]:
        """
        Returns:
            A List of active plugins.
        """
        return list(current_app.plugin_instances.keys())

class ConversionService:
    """A service providing functionality for conversion endpoints."""

    def __init__(
        self,
        conversion_repository: ConversionRepository,
        altspelling_repository: AltspellingRepository
    ):
        self._conversion_repository: ConversionRepository = conversion_repository
        self._altspelling_repository: AltspellingRepository = altspelling_repository

    def get_conversion_by_id(self, conversion_id: uuid) -> Conversion:
        """
        Retrieve a Conversion by id, from the database.

        Args:
            conversion_id (uuid): Id of the Conversion to query.

        Returns:
            Conversion: A Conversion object representing the queried database record.
        """
        return self._conversion_repository.get_by_id(conversion_id)

    def add_altspelling(self, altspelling: str) -> Altspelling:
        """
        Add an Altspelling to the database.

        Args:
            altspelling (str): Name of the Altspelling to add.

        Returns:
            Altspelling: An Altspelling object representing the added database record.
        """
        try:
            return self._altspelling_repository.add(altspelling)
        except IntegrityError:
            return self._altspelling_repository.get_by_name(altspelling)

    def convert(
        self,
        altspelling: str,
        to_altspell: bool,
        tradspell_text: str,
        altspell_text: str,
        save: bool
    ) -> Conversion:
        """
        Perform a conversion, optionallys saving it to the database.

        Args:
            altspelling (str): Name of the Altspelling plugin to use for conversion.
            to_altspell (bool): If true, convert tradspell -> altspell. Otherwise convert \
                altspell -> tradspell.
            tradspell_text (str): Tradspell text to convert to altspell text.
            altspell_text (str): Altspell text to convert to tradspell text.
            save (bool): If true, persist the conversion to the database.

        Returns:
            Altspelling: An Altspelling object representing the added database record.
        """

        # assign default save value
        if save is None:
            save = False

        # exception handling
        if altspelling is None:
            raise MissingKeyError("altspelling")

        if not isinstance(altspelling, str):
            raise InvalidTypeError("altspelling", str)

        if to_altspell is None:
            raise MissingKeyError("to_altspell")

        if not isinstance(to_altspell, bool):
            raise InvalidTypeError("to_altspell", bool)

        if to_altspell:
            if tradspell_text is None:
                raise MissingKeyError("tradspell_text")

            if not isinstance(tradspell_text, str):
                return InvalidTypeError("tradspell_text", str)
        else:
            if altspell_text is None:
                raise MissingKeyError("altspell_text")

            if not isinstance(altspell_text, str):
                raise InvalidTypeError("altspell_text", str)

        if to_altspell is True and tradspell_text == '':
            raise EmptyConversionError
        if to_altspell is False and altspell_text == '':
            raise EmptyConversionError

        selected_plugin = current_app.plugin_instances.get(altspelling)

        if selected_plugin is None:
            raise PluginUnavailableError(altspelling)

        # raises AltspellingNotFoundError if not found
        altspelling = self._altspelling_repository.get_by_name(altspelling)

        # get conversion functions
        convert_to_altspell = selected_plugin.convert_to_altspell
        convert_to_tradspell = selected_plugin.convert_to_tradspell

        conv_len_limit = current_app.config['CONVERSION_LENGTH_LIMIT']

        if to_altspell:
            tradspell_text = tradspell_text[:conv_len_limit]

            # raises NotImplementedFwdError if unimplemented
            altspell_text = convert_to_altspell(tradspell_text)
        else:
            altspell_text = altspell_text[:conv_len_limit]

            # raises NotImplementedBwdError if unimplemented
            tradspell_text = convert_to_tradspell(altspell_text)

        conversion = Conversion(
            to_altspell=to_altspell,
            tradspell_text=tradspell_text,
            altspell_text=altspell_text,
            altspelling_id=altspelling.id
        )

        conversion.altspelling = altspelling

        if save:
            conversion = self._conversion_repository.add(
                to_altspell=to_altspell,
                tradspell_text=tradspell_text,
                altspell_text=altspell_text,
                altspelling_id=altspelling.id,
            )

        return conversion
