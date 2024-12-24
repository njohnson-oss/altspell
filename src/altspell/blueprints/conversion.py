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
from flask import Blueprint, request, current_app
import pytz
from ..model import Altspelling, Conversion
from .. import db
from ..hcaptcha import require_hcaptcha


bp = Blueprint("conversions", __name__, url_prefix='/api')

@bp.route('/conversions', methods=['POST'])
@require_hcaptcha
def convert():
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
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775"
            "creation_date': "2020-10-21T05:39:20+0000"
            "altspelling": "lytspel",
            "to_altspell": True,
            "tradspell_text": "Hello world!",
            "altspell_text": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Converted English text is returned.
    - 400 Bad Request: JSON request is malformed or requested plugin method is unimplemented.
    """
    data = request.json

    save = data.get('save')
    to_altspell = data.get('to_altspell')
    tradspell_text = data.get('tradspell_text')
    altspell_text = data.get('altspell_text')
    altspelling = data.get('altspelling')

    # assign default save value
    if save is None:
        save = False

    if altspelling is None:
        return {'error': 'Missing key: altspelling'}, 400

    if not isinstance(altspelling, str):
        return {'error': 'Key must be a string: altspelling'}, 400

    altspelling_id = db.session.query(Altspelling).filter_by(name=altspelling).one_or_404().id

    if to_altspell is None:
        return {'error': 'Missing key: to_altspell'}, 400

    if not isinstance(to_altspell, bool):
        return {'error': 'Key must be a boolean: to_altspell'}, 400

    conv_len_limit = current_app.config['CONVERSION_LENGTH_LIMIT']

    # get conversion functions
    selected_plugin = current_app.plugin_instances.get(altspelling)

    if selected_plugin is None:
        return {'error': 'Selected plugin is not initialized'}

    convert_to_altspell = selected_plugin.convert_to_altspell
    convert_to_tradspell = selected_plugin.convert_to_tradspell

    if to_altspell:
        if tradspell_text is None:
            return {'error': 'Missing key: tradspell_text'}, 400
        if not isinstance(tradspell_text, str):
            return {'error': 'Key must be a string: to_altspell'}, 400

        tradspell_text = tradspell_text[:conv_len_limit]

        try:
            altspell_text = convert_to_altspell(tradspell_text)
        except NotImplementedError:
            return {
                'error': 'tradspell -> altspell conversion is not implemented for this plugin'
            }, 400
    else:
        if altspell_text is None:
            return {'error': 'Missing key: altspell_text'}, 400
        if not isinstance(altspell_text, str):
            return {'error': 'Key must be string: tradspell_text'}, 400

        altspell_text = altspell_text[:conv_len_limit]

        try:
            tradspell_text = convert_to_tradspell(altspell_text)
        except NotImplementedError:
            return {
                'error': 'altspell -> tradspell conversion is not implemented for this plugin'
            }, 400

    resp = {
        'altspelling': altspelling,
        'to_altspell': to_altspell,
        'tradspell_text': tradspell_text,
        'altspell_text': altspell_text
    }

    if save:
        conversion = Conversion(
            id=uuid.uuid4(),
            to_altspell=to_altspell,
            tradspell_text=tradspell_text,
            altspell_text=altspell_text,
            altspelling_id=altspelling_id
        )
        db.session.add(conversion)
        db.session.commit()

        resp['id'] = conversion.id
        resp['creation_date'] = pytz.utc.localize(conversion.creation_date).isoformat()

    return resp

@bp.route('/conversions/<uuid:conversion_id>', methods=['GET'])
def get_conversion(conversion_id):
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
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775"
            "creation_date": "2020-10-21T05:39:20+0000"
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
    conversion = db.session.query(Conversion).filter_by(id=conversion_id).one_or_404()

    resp = {
        'id': conversion.id,
        'creation_date': pytz.utc.localize(conversion.creation_date).isoformat(),
        'altspelling': conversion.altspelling.name,
        'to_altspell': conversion.to_altspell,
        'tradspell_text': conversion.tradspell_text,
        'altspell_text': conversion.altspell_text
    }

    return resp
