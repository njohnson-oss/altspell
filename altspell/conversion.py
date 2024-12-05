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

from flask import Blueprint, request, current_app
from .model import Altspelling, Conversion
from . import db

from .converter import convert_to_altspell
from .converter import convert_to_tradspell


bp = Blueprint("convert", __name__, url_prefix='/api')

@bp.route('/conversions', methods=['POST'])
def convert():
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

    conv_len_limit = current_app.config.get('CONVERSION_LENGTH_LIMIT')

    if to_altspell:
        if tradspell_text is None:
            return {'error': 'Missing key: tradspell_text'}, 400
        if not isinstance(tradspell_text, str):
            return {'error': 'Key must be a string: to_altspell'}, 400

        tradspell_text = tradspell_text[:conv_len_limit]
        altspell_text = convert_to_altspell(tradspell_text, altspelling)
    else:
        if altspell_text is None:
            return {'error': 'Missing key: altspell_text'}, 400
        if not isinstance(altspell_text, str):
            return {'error': 'Key must be string: tradspell_text'}, 400

        altspell_text = altspell_text[:conv_len_limit]
        tradspell_text = convert_to_tradspell(altspell_text, altspelling)

    resp = {
        'to_altspell': to_altspell,
        'tradspell_text': tradspell_text,
        'altspell_text': altspell_text,
        'altspelling': altspelling,
        'save': save
    }

    if save:
        conversion = Conversion(to_altspell, tradspell_text, altspell_text, altspelling_id)
        db.session.add(conversion)
        db.session.commit()

        resp['id'] = conversion.id
        resp['creation_date'] = conversion.creation_date

    return resp

@bp.route('/conversions/<uuid:conversion_id>', methods=['GET'])
def get_conversion(conversion_id):
    conversion = db.session.query(Conversion).one_or_404(id=conversion_id)

    resp = {
        'id': conversion.uuid,
        'creation_date': conversion.creation_date,
        'to_altspell': conversion.to_altspell,
        'tradspell_text': conversion.tradspell_text,
        'altspell_text': conversion.altspell_text,
        'altspelling': conversion.altspelling.name
    }

    return resp

@bp.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
