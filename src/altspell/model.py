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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from . import db


class UTCnow(expression.FunctionElement):
    type = db.DateTime()
    inherit_cache = True

@compiles(UTCnow, "postgresql")
def pg_utcnow(_element, _compiler, **_kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

@compiles(UTCnow, "mssql")
def ms_utcnow(_element, _compiler, **_kw):
    return "GETUTCDATE()"

@compiles(UTCnow, "sqlite")
def sqlite_utcnow(_element, _compiler, **_kw):
    return "(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))"

class Altspelling(db.Model):
    """
    A table containing the enabled alternate spellings of English.
    """
    __tablename__ = "altspelling"

    id: Mapped[int] = mapped_column(
        db.Integer,
        primary_key=True,
        doc='Sequence number representing alternative spelling of English.'
    )
    name: Mapped[str] = mapped_column(
        db.String,
        unique=True,
        doc='Name of alternative spelling of English.'
    )

    conversions: Mapped[List["Conversion"]] = relationship(
        back_populates="altspelling",
        doc='All conversions that use the alternative spelling of English.'
    )

class Conversion(db.Model):
    __tablename__ = "conversion"

    id: Mapped[uuid] = mapped_column(db.Uuid, primary_key=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(db.DateTime(),
                                                             server_default=UTCnow())
    to_altspell: Mapped[bool]
    tradspell_text: Mapped[str]
    altspell_text: Mapped[str]
    altspelling_id: Mapped[int] = mapped_column(db.ForeignKey('altspelling.id'))

    altspelling: Mapped["Altspelling"] = relationship(back_populates="conversions")
