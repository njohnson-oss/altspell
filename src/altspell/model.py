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


class utcnow(expression.FunctionElement):
    type = db.DateTime()
    inherit_cache = True

@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

@compiles(utcnow, "mssql")
def ms_utcnow(element, compiler, **kw):
    return "GETUTCDATE()"

@compiles(utcnow, "sqlite")
def sqlite_utcnow(element, compiler, **kw):
    return "(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))"

class Altspelling(db.Model):
    __tablename__ = "altspelling"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String, unique=True)

    conversions: Mapped[List["Conversion"]] = relationship(back_populates="altspelling")

class Conversion(db.Model):
    __tablename__ = "conversion"

    id: Mapped[uuid] = mapped_column(db.Uuid, primary_key=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(db.DateTime(),
                                                             server_default=utcnow())
    to_altspell: Mapped[bool]
    tradspell_text: Mapped[str]
    altspell_text: Mapped[str]
    altspelling_id: Mapped[int] = mapped_column(db.ForeignKey('altspelling.id'))

    altspelling: Mapped["Altspelling"] = relationship(back_populates="conversions")
