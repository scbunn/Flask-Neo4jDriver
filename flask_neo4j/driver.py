"""Neo4j Drive Flask Extension.


This module defines the `neo4j`_ `flask`_ extension that integrates the
official `python driver`_ with Flask.

This extension exposes the neo4j :class:`neo4j.v1.GraphDatabase` and other
utility functions to assist with the interaction of the graph database through
the python driver.


.. _neo4j: https://neo4j.com
.. _flask: http://flask.pocoo.org
.. _python driver: https://github.com/neo4j/neo4j-python-driver

"""
from neo4j.v1 import GraphDatabase, TRUST_ALL_CERTIFICATES
from flask import current_app
from .model import Node, Query

# import the correct stack depending on the version of Flask running.
# > 0.9 : _app_ctx_stack
# < 0.9 : _request_ctx_stack
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Neo4jDriver(object):
    """Database driver for Neo4j.

    This is the flask extension.

    Initialization.

    This extension can be initialized either directly or from a factory
    function.

    Direct Initialization

    .. code-block:: python

    from flask import Flask
    from flask.ext.neo4j import Neo4jDriver

    app = Flask(__name___)
    db = Neo4jDriver(app)

    Factory Function

    .. code-block:: python

    from flask import Flask
    from flask.ext.neo4j import Neo4jDriver

    db = Neo4jDriver()
    def create_app():
        app = Flask(__name__)
        db.init_app(app)
        return app


    .. note:
        This extension currently only supports basic auth tokens consisting
        of a username and password.

    """

    def __init__(self, app=None):
        """Neo4jDriver initialization.

        Args:
            app (:obj:`Flask`, optional): The flask application.  This defaults
                to `None` so that this extension can be late initialized to
                support application factories.

        """
        self.app = app
        self.Node = Node
        self.Query = Query
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Extension initialization.

        This is where extension initialization happens.  This method exists so
        that we can support direct initialization and late initialization with
        the same method.

        Args:
            app (:obj:`Flask`): The flask application.

        """
        app.config.setdefault('GRAPHDB', {
            'uri': 'bolt://localhost:7687',
            'user': 'neo4j',
            'pass': 'neo4j',
            'encrypted': True,
            'trust': TRUST_ALL_CERTIFICATES,
            'max_con_lifetime': 3600,
            'max_con_pool_size': 100,
            'lb': 0  # Least connected
        })

        # Initialize the Query class with our db
        self.Query.db = self

        # use newstyle teardown_appcontext if possible
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        """Teardown handler.

        `teardown()` is called when the application context is being
        destroyed.  Any cleanup for the extension should happen here.

        """
        ctx = stack.top

        # if the application context has a driver, close it.
        if hasattr(ctx, 'graphdb'):
            ctx.graphdb.close()

    def create_driver(self):
        """Create a new neo4j driver.

        The driver holds all the details of the database connection including
        the URI, credentials, and other configuration data.

        The driver maintains a pool of connections which are consumed by
        :class:`neo4j.v1.GraphDatabase.Session` instances.

        The type of driver is determined by the URI schemed passed at the time
        the driver is created.  The following schemes are supported:

            * bolt: `bolt://`
            * bolt+routing: `bolt+routing://`

        A driver is constructed based on the application configuration values
        that are present at the time of construction.  The following values
        are supported.

        Configuration values:
            GRAPHDB['uri'] (str): The URI for the graph database service.
            GRAPHDB['user'] (str): The user to connect as.
            GRAPHDB['pass'] (str): The password for the connected user.
            GRAPHDB['encrypted']: Boolean flag to determine if connection
                should be encrypted.
            GRAPHDB['trust'] (:obj:`int`): The trust level of certificates.
            GRAPHDB['max_con_lifetime'] (:obj:`int`): The maximum
                connection lifetime.
            GRAPHDB['max_con_pool_size'] (:obj:`int`): The max
                size of the connection pool.
            GRAPHDB['lb'] (:obj:`int`): The default load balancing
                strategy.

        For more information about configuration values, look at the
        `default_config` dictionary in the :mod:`neo4j.v1.config`

        """
        config = current_app.config['GRAPHDB']
        current_app.logger.debug('Graph DB Config: {}'.format(config))
        driver = GraphDatabase.driver(
            config['uri'],
            auth=(config['user'], config['pass']),
            encrypted=config['encrypted'],
            trust=config['trust'],
            max_connection_lifetime=config['max_con_lifetime'],
            max_connection_pool_size=config['max_con_pool_size'],
            load_balancing_strategy=config['lb']
        )
        return driver

    @property
    def driver(self):
        """Return the instance of the driver.

        Return the instance of the driver attached to the application.

        """
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'graphdb'):
                ctx.graphdb = self.create_driver()
            return ctx.graphdb

    @property
    def session(self):
        """Create and return a session.

        Construct a :class:`neo4j.v1.GraphDatabase.Session` using the current
        applications driver.

        Sessions are logical contexts for transactional units of work.  They
        *are not* thread safe and are usually short lived.
        """
        return self.driver.session()
