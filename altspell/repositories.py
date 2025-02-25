'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
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

from contextlib import AbstractAsyncContextManager
from typing import Callable
import uuid
from sqlalchemy.orm import Session, selectinload
from .model import SpellingSystem, Translation
from .exceptions import TranslationNotFoundError, SpellingSystemNotFoundError


class TranslationRepository:
    """Repository for database operations related to translations."""
    def __init__(
        self,
        session_factory: Callable[
            ...,
            AbstractAsyncContextManager[Session]
        ]
    ) -> None:
        self.session_factory = session_factory

    def add(
        self,
        forward: bool,
        traditional_text: str,
        respelled_text: str,
        spelling_system_id: int
    ) -> Translation:
        """
        Add a translation to the database.

        Args:
            forward (bool): True if translated to the alternative spelling system. False if \
                translated to traditional English spelling.
            traditional_text (str): Text in traditional English spelling.
            respelled_text (str): Text in the alternative English spelling system.
            spelling_system_id (int): Id of the alternative spelling system.

        Returns:
            Translation: The translation object added to the database.
        """
        with self.session_factory() as session:
            translation = Translation(
                id=uuid.uuid4(),
                forward=forward,
                traditional_text=traditional_text,
                respelled_text=respelled_text,
                spelling_system_id=spelling_system_id
            )
            session.add(translation)
            session.commit()
            translation = (
                session.query(Translation)
                .options(selectinload(Translation.spelling_system))
                .filter(Translation.id == translation.id)
                .first()
            )
            return translation

    def get_by_id(self, translation_id: uuid) -> Translation:
        """
        Retrieve a translation by id.

        Args:
            translation_id (uuid): Id of the requested translation.

        Returns:
            Translation: The translation object corresponding to translation_id.
        """
        with self.session_factory() as session:
            translation = (
                session.query(Translation)
                .options(selectinload(Translation.spelling_system))
                .filter(Translation.id == translation_id)
                .first()
            )
            if not translation:
                raise TranslationNotFoundError(translation_id)
            return translation

class SpellingSystemRepository:
    """Repository for database operations related to alternative spelling systems."""
    def __init__(
        self,
        session_factory: Callable[
            ...,
            AbstractAsyncContextManager[Session]
        ]
    ) -> None:
        self.session_factory = session_factory

    def add(self, spelling_system_name: str) -> SpellingSystem:
        """
        Add an alternative spelling system.

        Args:
            spelling_system_name (str): Name of the alternative spelling system.

        Returns:
            SpellingSystem: The alternative spelling system object added to the database.
        """
        with self.session_factory() as session:
            spelling_system = SpellingSystem(name=spelling_system_name)
            session.add(spelling_system)
            session.commit()
            session.refresh(spelling_system)
            return spelling_system

    def get_all(self):
        """Retrieve a list of enabled alternative spelling systems."""
        with self.session_factory() as session:
            return session.query(SpellingSystem).all()

    def get_by_name(self, spelling_system_name: str) -> SpellingSystem:
        """
        Retrieve an alternative spelling system object by alternative spelling system name.

        Args:
            spelling_system_name (str): Name of the alternative spelling system.

        Returns:
            SpellingSystem: The alternative spelling system object corresponding to \
                spelling_system_name.
        """
        with self.session_factory() as session:
            spelling_system = (
                session.query(SpellingSystem)
                .filter(SpellingSystem.name == spelling_system_name)
                .first()
            )
            if not spelling_system:
                raise SpellingSystemNotFoundError
            return spelling_system
