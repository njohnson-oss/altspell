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

import uuid
import datetime
from typing import List
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from .database import Base


class UTCnow(expression.FunctionElement):
    """A construct representing the current UTC timestamp."""
    type = DateTime()
    inherit_cache = True

@compiles(UTCnow, "postgresql")
def pg_utcnow(_element, _compiler, **_kw):
    """Compiles the `UTCnow` expression to the PostgreSQL-specific SQL syntax for retrieving the
    UTC timestamp."""
    return "date_trunc('second', TIMEZONE('utc', CURRENT_TIMESTAMP))"

@compiles(UTCnow, "mssql")
def ms_utcnow(_element, _compiler, **_kw):
    """Compiles the `UTCnow` expression to the Microsoft SQL-specific SQL syntax for retrieving the
    UTC timestamp."""
    return "GETUTCDATE() AS SMALLDATETIME"

@compiles(UTCnow, "sqlite")
def sqlite_utcnow(_element, _compiler, **_kw):
    """Compiles the `UTCnow` expression to the Sqlite-specific SQL syntax for retrieving the UTC
    timestamp."""
    return "(STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW'))"

class Altspelling(Base):
    """A table containing the enabled alternate spellings of English."""
    __tablename__ = "altspelling"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        doc='Sequence number representing alternative spelling of English.'
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        doc='Name of alternative spelling of English.'
    )

    conversions: Mapped[List["Conversion"]] = relationship(
        back_populates="altspelling",
        doc='All conversions that use the alternative spelling of English.'
    )

class Conversion(Base):
    """A table containing the saved conversions."""
    __tablename__ = "conversion"

    id: Mapped[uuid] = mapped_column(
        Uuid,
        primary_key=True,
        doc='Sequence number representing conversion.'
    )
    creation_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        server_default=UTCnow(),
        doc='DateTime representing when the conversion was inserted into the database.'
    )
    to_altspell: Mapped[bool] = mapped_column(
        Boolean,
        doc='Boolean representing which direction the conversion occurred in. I.e: Either ' \
            'traditional English spelling => alternative English spelling or alternative ' \
            'English spelling => traditional English spelling.'
    )
    tradspell_text: Mapped[str] = mapped_column(
        String,
        doc='Text in traditional English spelling.'
    )
    altspell_text: Mapped[str] = mapped_column(
        String,
        doc='Text in alternative English spelling.'
    )
    altspelling_id: Mapped[int] = mapped_column(
        ForeignKey('altspelling.id'),
        doc='Sequence number representing alternative spelling of English.'
    )

    altspelling: Mapped["Altspelling"] = relationship(
        back_populates="conversions",
        doc='The alternative spelling of English that was used by the conversion.'
    )
