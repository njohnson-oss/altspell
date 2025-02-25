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

import uuid
from typing import List
from flask import current_app
from sqlalchemy.exc import IntegrityError
from .repositories import TranslationRepository, AltspellingRepository
from .model import Altspelling, Translation
from .exceptions import (
    MissingKeyError, InvalidTypeError, EmptyTranslationError, PluginUnavailableError
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

class TranslationService:
    """A service providing functionality for translation endpoints."""

    def __init__(
        self,
        translation_repository: TranslationRepository,
        altspelling_repository: AltspellingRepository
    ):
        self._translation_repository: TranslationRepository = translation_repository
        self._altspelling_repository: AltspellingRepository = altspelling_repository

    def get_translation_by_id(self, translation_id: uuid) -> Translation:
        """
        Retrieve a Translation by id, from the database.

        Args:
            translation_id (uuid): Id of the Translation to query.

        Returns:
            Translation: A Translation object representing the queried database record.
        """
        return self._translation_repository.get_by_id(translation_id)

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

    def translate(
        self,
        altspelling: str,
        to_altspell: bool,
        text: str,
        save: bool
    ) -> Translation:
        """
        Perform a translation, optionally saving it to the database.

        Args:
            altspelling (str): Name of the Altspelling plugin to use for translation.
            to_altspell (bool): If true, translate tradspell -> altspell. Otherwise translate \
                altspell -> tradspell.
            text (str): Text to be translated.
            save (bool): If true, persist the translation to the database.

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

        if text is None:
            raise MissingKeyError("text")

        if not isinstance(text, str):
            raise InvalidTypeError("text", str)

        if text == '':
            raise EmptyTranslationError

        selected_plugin = current_app.plugin_instances.get(altspelling)

        if selected_plugin is None:
            raise PluginUnavailableError(altspelling)

        # raises AltspellingNotFoundError if not found
        altspelling = self._altspelling_repository.get_by_name(altspelling)

        # get translation functions
        translate_to_altspell = selected_plugin.translate_to_altspell
        translate_to_tradspell = selected_plugin.translate_to_tradspell

        translation_length_limit = current_app.config['TRANSLATION_LENGTH_LIMIT']

        text = text[:translation_length_limit]

        if to_altspell:
            tradspell_text = text

            # raises NotImplementedFwdError if unimplemented
            altspell_text = translate_to_altspell(text)
        else:
            # raises NotImplementedBwdError if unimplemented
            tradspell_text = translate_to_tradspell(text)

            altspell_text = text

        translation = Translation(
            to_altspell=to_altspell,
            tradspell_text=tradspell_text,
            altspell_text=altspell_text,
            altspelling_id=altspelling.id
        )

        translation.altspelling = altspelling

        if save:
            translation = self._translation_repository.add(
                to_altspell=to_altspell,
                tradspell_text=tradspell_text,
                altspell_text=altspell_text,
                altspelling_id=altspelling.id,
            )

        return translation
