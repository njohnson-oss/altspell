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
from .model import Altspelling

from .converter import convert_text


bp = Blueprint("convert", __name__, url_prefix='/api')

@bp.route('/convert', methods=['POST'])
def convert():
    data = request.json

    to_altspell = data.get('to_altspell')
    tradspell_text = data.get('tradspell_text')
    altspell_text = data.get('altspell_text')
    altspelling = data.get('altspelling')

    # error handling
    if altspelling is None:
        return {'error': 'Missing key: altspelling'}, 400

    if not isinstance(altspelling, str):
        return {'error': 'Key must be a string: altspelling'}, 400

    # just check that the record exists for now
    Altspelling.query.filter_by(altspelling=altspelling).one_or_404()

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
    else:
        if altspell_text is None:
            return {'error': 'Missing key: altspell_text'}, 400
        if not isinstance(altspell_text, str):
            return {'error': 'Key must be string: tradspell_text'}, 400

        altspell_text = altspell_text[:conv_len_limit]

    resp = convert_text(tradspell_text, altspell_text, altspelling, to_altspell)

    return resp

@bp.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
