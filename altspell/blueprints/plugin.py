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

from flask import Blueprint, jsonify, current_app


bp = Blueprint("plugins", __name__, url_prefix='/api')

@bp.route('/plugins', methods=['GET'])
def get_plugins():
    """
    Endpoint that returns a list of enabled plugins.

    This endpoint accepts a GET request and returns a list of enabled plugins in the JSON Response.

    Returns:
        Response: A JSON Response object containing a list of enabled plugins.

    Example:

        Request:
        GET /api/plugins

        Response:
        GET /api/plugins
        Response Body: {
            "plugins": [
                 "lytspel",
                 "soundspel"
            ]
        }

    HTTP Status Codes:
    - 200 OK: List of plugins is returned.
    """
    plugins = list(current_app.plugin_instances.keys())

    resp = {
        'plugins': plugins
    }

    return jsonify(resp)
