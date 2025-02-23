'''
    Altspell  Flask web app for converting traditional English spelling to
    an alternative spelling
    Copyright (C) 2024-2025  Nicholas Johnson

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
from flask import Blueprint, request, current_app
import pytz
from dependency_injector.wiring import inject, Provide
from ..model import Altspelling, Conversion
from ..hcaptcha import require_hcaptcha
from ..containers import Container
from ..services import ConversionService
from ..exceptions import NotFoundError, MissingKeyError, InvalidTypeError, EmptyConversionError, PluginUnavailableError, AltspellingNotFoundError


bp = Blueprint("conversions", __name__, url_prefix='/api')

@bp.route('/conversions', methods=['POST'])
@require_hcaptcha
@inject
def convert(
    conversion_service: ConversionService = Provide[Container.conversion_service]
):
    """
    Endpoint to convert traditional English spelling to alternative English spelling and vice
    versa.

    This endpoint accepts a POST request with a JSON request body and returns the converted English
    text in the JSON Response. Optionally, it saves the resulting conversion in the database.

    JSON Request Parameters:
    - altspelling (str): Name of conversion Plugin.
    - to_altspell (bool): Indicates the direction of conversion.
    - tradspell_text (str): Text in traditional English spelling (necessary if to_altspell is True).
    - altspell_text (str): Text in alternative English spelling (necessary if to_altspell is False).
    - save (bool): Indicates whether save the resulting conversion.

    JSON Response Parameters:
    - id (uuid): ID of the conversion. (only if 'save' was True in the request)
    - creation_date (DateTime): Date and time conversion was inserted into the database. (only if
                                'save' was True in the request)
    - altspelling (str): Name of conversion Plugin.
    - to_altspell (bool): Indicates the direction of conversion.
    - tradspell_text (str): Text in traditional English spelling (necessary if to_altspell is True).
    - altspell_text (str): Text in alternative English spelling (necessary if to_altspell is False).

    Returns:
        Response: A JSON Response object containing the converted English text.

    Example:

        Request:
        POST /api/conversions
        Request Body: {
            "altspelling": "lytspel",
            "to_altspell': True,
            "tradspell_text": "Hello world!",
            "save": True
        }

        Response:
        POST /api/conversions
        Response Body: {
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775",
            "creation_date': "2020-10-21T05:39:20+00:00",
            "altspelling": "lytspel",
            "to_altspell": True,
            "tradspell_text": "Hello world!",
            "altspell_text": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Converted English text is returned.
    - 400 Bad Request: JSON request is malformed or requested plugin method is unavailable.
    """
    data = request.json

    save = data.get('save')
    altspelling = data.get('altspelling')
    to_altspell = data.get('to_altspell')
    tradspell_text = data.get('tradspell_text')
    altspell_text = data.get('altspell_text')

    try:
        conversion = conversion_service.convert(
            altspelling,
            to_altspell,
            tradspell_text,
            altspell_text,
            save
        )
    except (
        MissingKeyError,
        InvalidTypeError,
        EmptyConversionError,
        NotImplementedError,
        PluginUnavailableError,
        AltspellingNotFoundError
    ) as e:
        return {'error': str(e)}, 400

    resp = {
        'altspelling': conversion.altspelling.name,
        'to_altspell': conversion.to_altspell,
        'tradspell_text': conversion.tradspell_text,
        'altspell_text': conversion.altspell_text
    }

    if save:
        resp['id'] = conversion.id
        resp['creation_date'] = pytz.utc.localize(conversion.creation_date).isoformat()

    return resp

@bp.route('/conversions/<uuid:conversion_id>', methods=['GET'])
@inject
def get_conversion(
    conversion_id: uuid,
    conversion_service: ConversionService = Provide[Container.conversion_service]
):
    """
    Endpoint to get saved conversion.

    This endpoint accepts a GET request with the appended conversion ID (uuid).

    JSON Response Parameters:
    - id (uuid): ID of the conversion.
    - creation_date (DateTime): Date and time conversion was inserted into the database.
    - altspelling (str): Name of conversion Plugin.
    - to_altspell (bool): Indicates the direction of conversion.
    - tradspell_text (str): Text in traditional English spelling (necessary if to_altspell is True).
    - altspell_text (str): Text in alternative English spelling (necessary if to_altspell is False).

    Returns:
        Response: A JSON Response object containing the converted English text.

    Example:

        Request:
        GET /api/conversions/7d9be066-6a0b-4459-9242-86dce2df6775

        Response:
        GET /api/conversions
        Response Body: {
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775",
            "creation_date": "2020-10-21T05:39:20+0000",
            "altspelling": "lytspel",
            "to_altspell": True,
            "tradspell_text": "Hello world!",
            "altspell_text": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Converted English text is returned.
    - 400 Bad Request: Conversion ID is not a UUID.
    - 404 Not Found: Conversion not found.
    """
    try:
        conversion = conversion_service.get_conversion_by_id(conversion_id)
    except NotFoundError:
        return {'error': 'Conversion not found'}, 404

    resp = {
        'id': conversion.id,
        'creation_date': pytz.utc.localize(conversion.creation_date).isoformat(),
        'altspelling': conversion.altspelling.name,
        'to_altspell': conversion.to_altspell,
        'tradspell_text': conversion.tradspell_text,
        'altspell_text': conversion.altspell_text
    }

    return resp
