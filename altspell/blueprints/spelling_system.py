'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
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

from flask import Blueprint, jsonify
from dependency_injector.wiring import Provide, inject
from ..services import SpellingSystemService
from ..containers import Container


bp = Blueprint("spelling_systems", __name__, url_prefix='/api/v1')

@bp.route('/spelling-systems', methods=['GET'])
@inject
def get_spelling_systems(spelling_system_service: SpellingSystemService = \
    Provide[Container.spelling_system_service]):
    """
    Endpoint that returns a list of enabled spelling systems.

    This endpoint accepts a GET request and returns a list of enabled spelling systems in the \
        JSON Response.

    Returns:
        Response: A JSON Response object containing a list of enabled spelling systems.

    Example:

        Request:
        GET /api/v1/spelling-systems

        Response:
        GET /api/v1/spelling-systems
        Response Body: [
            "lytspel",
            "soundspel"
        ]

    HTTP Status Codes:
    - 200 OK: List of spelling systems is returned.
    """
    spelling_systems = spelling_system_service.get_spelling_systems()

    return jsonify(spelling_systems)
