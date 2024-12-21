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

from functools import wraps
import requests
from flask import current_app, request, jsonify


def _verify_hcaptcha(token):
    secret_key = current_app.config['HCAPTCHA_SECRET_KEY']
    verification_url = 'https://api.hcaptcha.com/siteverify'

    # prepare payload for POST request
    payload = {
        'secret': secret_key,
        'response': token
    }

    resp = requests.post(verification_url, data=payload, timeout=10)

    return resp.json().get('success') is True

def require_hcaptcha(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.config['ENABLE_HCAPTCHA'] is not True:
            return func(*args, **kwargs)

        data = request.json
        hcaptcha_token = data.get('hcaptcha_token')

        if not hcaptcha_token:
            return jsonify({"error": "hCaptcha token is missing"}), 400

        # verify hCaptcha token
        if _verify_hcaptcha(hcaptcha_token) is False:
            return jsonify({"error": "hCaptcha verification failed"}), 400

        # if valid hCaptcha, proceed with the request
        return func(*args, **kwargs)

    return wrapper
