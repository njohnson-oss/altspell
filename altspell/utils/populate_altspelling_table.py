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

from dependency_injector.wiring import inject, Provide
from ..services import ConversionService
from ..containers import Container


@inject
def populate_altspelling_table(
    altspelling: str,
    conversion_service: ConversionService = Provide[Container.conversion_service]
):
    """Populate altspelling table with plugin"""
    conversion_service.add_altspelling(altspelling)
