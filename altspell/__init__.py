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

import importlib
import pkgutil
import os
from flask import Flask
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from .plugin import PluginBase


AVAILABLE_PLUGINS = {
    name.removeprefix('altspell_'): importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('altspell_')
}

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
        ENABLED_PLUGINS = AVAILABLE_PLUGINS.keys(),
        # disable CAPTCHA for test purposes
        ENABLE_HCAPTCHA = False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    with app.app_context():
        from .containers import Container  # pylint: disable=import-outside-toplevel

        # create container for dependency injection
        container = Container()

    app.container = container

    # allow CORS for all domains on all routes
    CORS(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.plugin_instances = {}

    for plugin in app.config['ENABLED_PLUGINS']:
        if plugin in AVAILABLE_PLUGINS:
            plugin_mod = AVAILABLE_PLUGINS[plugin]

            # validate plugin implementation
            if not hasattr(plugin_mod, 'Plugin'):
                app.logger.error(
                    'Enabled plugin excluded for missing "Plugin" attribute: %s', plugin
                )
                continue

            if not issubclass(plugin_mod.Plugin, PluginBase):
                app.logger.error(
                    'Enabled plugin excluded for not being a subclass of PluginBase: %s', plugin
                )
                continue

            with app.app_context():
                from .utils.populate_altspelling_table import populate_altspelling_table  # pylint: disable=import-outside-toplevel
                populate_altspelling_table(plugin)

            # initialize plugin
            app.logger.info('Initializing plugin: %s...', plugin)
            plugin_instance = plugin_mod.Plugin()
            app.plugin_instances[plugin] = plugin_instance
        else:
            app.logger.warning('Enabled plugin is not available: %s', plugin)

    # apply the blueprints to the app
    from .blueprints import conversion  # pylint: disable=import-outside-toplevel
    app.register_blueprint(conversion.bp)

    from .blueprints import plugin  # pylint: disable=import-outside-toplevel
    app.register_blueprint(plugin.bp)

    return app
