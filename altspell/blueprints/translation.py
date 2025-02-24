'''
    Altspell  Flask web app for translating traditional English spelling to an alternative spelling
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
from flask import Blueprint, request
import pytz
from dependency_injector.wiring import inject, Provide
from ..utils.hcaptcha import require_hcaptcha
from ..containers import Container
from ..services import TranslationService
from ..exceptions import (
    NotFoundError,
    MissingKeyError,
    InvalidTypeError,
    EmptyTranslationError,
    PluginUnavailableError,
    AltspellingNotFoundError
)


bp = Blueprint("translations", __name__, url_prefix='/api')

@bp.route('/translations', methods=['POST'])
@require_hcaptcha
@inject
def translate(
    translation_service: TranslationService = Provide[Container.translation_service]
):
    """
    Endpoint to translate traditional English spelling to alternative English spelling and vice
    versa.

    This endpoint accepts a POST request with a JSON request body and returns the translated
    English text in the JSON Response. Optionally, it saves the resulting translation in the
    database.

    JSON Request Parameters:
    - altspelling (str): Name of translation Plugin.
    - to_altspell (bool): Indicates the direction of translation.
    - tradspell_text (str): Text in traditional English spelling (necessary if to_altspell is \
        True).
    - altspell_text (str): Text in alternative English spelling (necessary if to_altspell is \
        False).
    - save (bool): Indicates whether save the resulting translation.

    JSON Response Parameters:
    - id (uuid): ID of the translation. (only if 'save' was True in the request)
    - creation_date (DateTime): Date and time translation was inserted into the database. (only if
                                'save' was True in the request)
    - altspelling (str): Name of translation Plugin.
    - to_altspell (bool): Indicates the direction of translation.
    - tradspell_text (str): Text in traditional English spelling (necessary if to_altspell is True).
    - altspell_text (str): Text in alternative English spelling (necessary if to_altspell is False).

    Returns:
        Response: A JSON Response object containing the translated English text.

    Example:

        Request:
        POST /api/translations
        Request Body: {
            "altspelling": "lytspel",
            "to_altspell': True,
            "tradspell_text": "Hello world!",
            "save": True
        }

        Response:
        POST /api/translations
        Response Body: {
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775",
            "creation_date": "2020-10-21T05:39:20+00:00",
            "altspelling": "lytspel",
            "to_altspell": True,
            "tradspell_text": "Hello world!",
            "altspell_text": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Translated English text is returned.
    - 400 Bad Request: JSON request is malformed or requested plugin method is unavailable.
    """
    data = request.json

    save = data.get('save')
    altspelling = data.get('altspelling')
    to_altspell = data.get('to_altspell')
    tradspell_text = data.get('tradspell_text')
    altspell_text = data.get('altspell_text')

    try:
        translation = translation_service.translate(
            altspelling,
            to_altspell,
            tradspell_text,
            altspell_text,
            save
        )
    except (
        MissingKeyError,
        InvalidTypeError,
        EmptyTranslationError,
        NotImplementedError,
        PluginUnavailableError,
        AltspellingNotFoundError
    ) as e:
        return {'error': str(e)}, 400

    resp = {
        'altspelling': translation.altspelling.name,
        'to_altspell': translation.to_altspell,
        'tradspell_text': translation.tradspell_text,
        'altspell_text': translation.altspell_text
    }

    if save:
        resp['id'] = translation.id
        resp['creation_date'] = pytz.utc.localize(translation.creation_date).isoformat()

    return resp

@bp.route('/translation/<uuid:translation_id>', methods=['GET'])
@inject
def get_translation(
    translation_id: uuid,
    translation_service: TranslationService = Provide[Container.translation_service]
):
    """
    Endpoint to get saved translation.

    This endpoint accepts a GET request with the appended translation ID (uuid).

    JSON Response Parameters:
    - id (uuid): ID of the translation.
    - creation_date (DateTime): Date and time translation was inserted into the database.
    - altspelling (str): Name of translation Plugin.
    - to_altspell (bool): Indicates the direction of translation.
    - tradspell_text (str): Text in traditional English spelling (necessary if to_altspell is True).
    - altspell_text (str): Text in alternative English spelling (necessary if to_altspell is False).

    Returns:
        Response: A JSON Response object containing the translated English text.

    Example:

        Request:
        GET /api/translations/7d9be066-6a0b-4459-9242-86dce2df6775

        Response:
        GET /api/translations
        Response Body: {
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775",
            "creation_date": "2020-10-21T05:39:20+0000",
            "altspelling": "lytspel",
            "to_altspell": True,
            "tradspell_text": "Hello world!",
            "altspell_text": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Translated English text is returned.
    - 400 Bad Request: Translation ID is not a UUID.
    - 404 Not Found: Translation not found.
    """
    try:
        translation = translation_service.get_translation_by_id(translation_id)
    except NotFoundError:
        return {'error': 'Translation not found'}, 404

    resp = {
        'id': translation.id,
        'creation_date': pytz.utc.localize(translation.creation_date).isoformat(),
        'altspelling': translation.altspelling.name,
        'to_altspell': translation.to_altspell,
        'tradspell_text': translation.tradspell_text,
        'altspell_text': translation.altspell_text
    }

    return resp
