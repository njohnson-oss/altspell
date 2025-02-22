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

from typing import List
from flask import current_app


class PluginService:
    """A service providing functionality for plugin endpoints."""

    @staticmethod
    def get_plugins() -> List[str]:
        """Returns a list of active plugins"""
        return list(current_app.plugin_instances.keys())
