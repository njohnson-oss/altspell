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

from contextlib import AbstractAsyncContextManager
from typing import Callable
import uuid
from sqlalchemy.orm import Session, selectinload
from .model import Altspelling, Conversion
from .exceptions import ConversionNotFoundError, AltspellingNotFoundError


class ConversionRepository:

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
        to_altspell: bool,
        tradspell_text: str,
        altspell_text: str,
        altspelling_id: int
    ) -> Conversion:
        with self.session_factory() as session:
            conversion = Conversion(
                id=uuid.uuid4(),
                to_altspell=to_altspell,
                tradspell_text=tradspell_text,
                altspell_text=altspell_text,
                altspelling_id=altspelling_id
            )
            session.add(conversion)
            session.commit()
            conversion_with_altspelling = (
                session.query(Conversion)
                .options(selectinload(Conversion.altspelling))
                .filter(Conversion.id == conversion.id)
                .first()
            )
            return conversion_with_altspelling

    def get_by_id(self, conversion_id: uuid) -> Conversion:
        with self.session_factory() as session:
            conversion = (
                session.query(Conversion)
                .options(selectinload(Conversion.altspelling))
                .filter(Conversion.id == conversion_id)
                .first()
            )
            if not conversion:
                raise ConversionNotFoundError(conversion_id)
            return conversion

class AltspellingRepository:

    def __init__(
        self,
        session_factory: Callable[
            ...,
            AbstractAsyncContextManager[Session]
        ]
    ) -> None:
        self.session_factory = session_factory

    def add(self, altspelling_name: str) -> Altspelling:
        with self.session_factory() as session:
            altspelling = Altspelling(name=altspelling_name)
            session.add(altspelling)
            session.commit()
            session.refresh(altspelling)
            return altspelling

    def get_all(self):
        with self.session_factory() as session:
            return session.query(Altspelling).all()

    def get_by_name(self, altspelling_name: str) -> Altspelling:
        with self.session_factory() as session:
            altspelling = (
                session.query(Altspelling)
                .filter(Altspelling.name == altspelling_name)
                .first()
            )
            if not altspelling:
                raise AltspellingNotFoundError
            return altspelling
