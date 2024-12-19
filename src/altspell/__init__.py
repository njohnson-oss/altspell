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

import importlib
import pkgutil
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


AVAILABLE_PLUGINS = {
    name.removeprefix('altspell_'): importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('altspell_')
}

db = SQLAlchemy()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the app instance path
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'altspell.db'),
        # maximum number of characters accepted for conversion
        CONVERSION_LENGTH_LIMIT = 20000,
        # enable all plugins by default
        ENABLED_PLUGINS = AVAILABLE_PLUGINS.keys()
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from . import model

    with app.app_context():
        # create database tables
        db.create_all()

    app.plugin_instances = {}

    for plugin in app.config.get('ENABLED_PLUGINS'):
        if plugin in AVAILABLE_PLUGINS:
            altspelling = model.Altspelling(name=plugin)

            # populate altspelling table with enabled plugin
            with app.app_context():
                try:
                    db.session.add(altspelling)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

            # initialize plugin
            app.logger.info('Initializing plugin: %(plugin)...')
            plugin_instance = getattr(AVAILABLE_PLUGINS.get(plugin), 'Plugin')()
            app.plugin_instances[plugin] = plugin_instance
        else:
            app.logger.warning('Enabled plugin is not available: %(plugin)')

    # apply the blueprints to the app
    from .blueprints import conversion
    app.register_blueprint(conversion.bp)

    from .blueprints import plugin
    app.register_blueprint(plugin.bp)

    return app
