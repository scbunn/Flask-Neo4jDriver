"""Py.Test setup and configuration.

This module defines default fixtures and common test functions.

"""
import pytest
import os
from flask import Flask
from flask.ext.neo4j import Neo4jDriver


db = Neo4jDriver()


def create_app():
    """Application factory to create a new flask app."""
    app = Flask(__name__)
    app.config['DEBUG'] = True
    db.init_app(app)
    return app


@pytest.fixture
def Driver():
    """Return the Neo4jDriver Database driver."""
    global db
    return db


@pytest.fixture
def app():
    """Define the test application.

    Fixture used by Flask-PyTest `client` fixture
    """
    app = create_app()
    return app


@pytest.fixture
def testclient(request):
    """Test Client fixture.

    Return a test client based on the config present in the `request`.

    Usage:

        .. code-block:: python

        @pytest.mark.parametrize('testclient', [{}], indirect=True)
        def test_foo(testclient):
            testclient.get(...)


    """
    print(request.param)
    app = Flask(__name__)
    app.config['GRAPHDB'] = request.param
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.init_app(app)

    ctx = app.app_context()
    ctx.push()
    yield (client, request.param)
    ctx.pop()


@pytest.fixture
def CIGraphCreds():
    data = {
        'uri': os.getenv('GRAPHDB_URI', 'bolt://localhost:7687'),
        'user': os.getenv('GRAPHDB_USER', 'neo4j'),
        'pass': os.getenv('GRAPHDB_PASS', 'neo4j'),
        'encrypted': True,
        'trust': 2,
        'max_con_lifetime': 300,
        'max_con_pool_size': 100,
        'lb': 0
    }
    return data
