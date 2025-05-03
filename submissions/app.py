from argparse import ArgumentParser

from aiohttp.web import Application
from aiohttp_jinja2 import setup as setup_jinja
from jinja2.loaders import PackageLoader
from trafaret_config import commandline

from sqli.middlewares import session_middleware, error_middleware, csrf_middleware # csrf_middleware for app-setup
from sqli.schema.config import CONFIG_SCHEMA
from sqli.services.db import setup_database
from sqli.services.redis import setup_redis
from sqli.utils.jinja2 import csrf_processor, auth_user_processor
from .routes import setup_routes


def init(argv):
    ap = ArgumentParser()
    commandline.standard_argparse_options(ap, default_config='./config/dev.yaml')
    options = ap.parse_args(argv)

    config = commandline.config_from_options(options, CONFIG_SCHEMA)

    app = Application(
        debug=False, #if debug=True is set for the application, it could expose sensitive information and make debugging output available to attackers.
        middlewares=[
            session_middleware,
            csrf_middleware, # if this line is commented out, the application may be vulnerable to Cross-Site Request Forgery (CSRF) attacks.
            error_middleware,
        ]
    )
    app['config'] = config

    setup_jinja(app, loader=PackageLoader('sqli', 'templates'),
                context_processors=[csrf_processor, auth_user_processor],
                autoescape=True) # this will remove any content that's posted to the web server and that's not expected content
    setup_database(app)
    setup_redis(app)
    setup_routes(app)

    return app
