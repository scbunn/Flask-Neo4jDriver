"""Neo4jDriver Unit Tests.


This module defines the unit tests for the :class:`Neo4jDriver` class.

"""
import pytest
import neo4j.v1
from flask import Flask, current_app
from flask.ext.neo4j import Neo4jDriver

pytestmark = pytest.mark.unittests


@pytest.mark.parametrize("option, value", [
    ('uri', 'bolt://localhost:7687'),
    ('user', 'neo4j'),
    ('pass', 'neo4j'),
    ('encrypted', True),
    ('max_con_lifetime', 3600),
    ('max_con_pool_size', 100),
    ('lb', 0),
    ('trust', neo4j.v1.TRUST_ALL_CERTIFICATES)
])
def test_default_extension_configuration(client, option, value):
    """Test the default configuration values.

    Assert the default configuration values are set as expected.

    """
    assert current_app.config['GRAPHDB'].get(option, '') == value



@pytest.mark.parametrize('testclient', [
    {'uri': 'bolt+routing://testhost:1'},
    {'user': 'citest'},
    {'pass': 'foobar'},
    {'encrypted': False},
    {'trust': 9999},
    {'max_con_lifetime': 1},
    {'max_con_pool_size': 1},
    {'lb': 1}
], ids=[
    'uri',
    'user',
    'pass',
    'encrypted',
    'trust',
    'max_con_lifetime',
    'max_con_pool_size',
    'lb' ], indirect=True)
def test_configuration_option_override(testclient):
    """Test configuration option override.

    Assert the extension uses custom configuration values if set.

    """
    _, request = testclient
    conf = current_app.config['GRAPHDB']
    print(conf)
    assert conf == request


def test_neo4jdriver_direct_initialization():
    """Test Neo4jDriver direct initialization.

    Assert that :class:`Neo4jDriver` can be directly initialized.

    """
    app = Flask(__name__)
    db = Neo4jDriver(app)
    assert len(app.config['GRAPHDB'].keys()) > 1


@pytest.mark.neo4j
def test_driver_can_connect_successfully(client, Driver, CIGraphCreds):
    """Test the driver can initiate a connection.

    Assert the driver is able to initiate communication to the neo4j server.

    """
    current_app.config['GRAPHDB'] = CIGraphCreds
    assert Driver.create_driver()  # if a valid object returned, we connected


@pytest.mark.neo4j
def test_driver_connection_failed_with_bad_credentials(client, Driver,
                                                       CIGraphCreds):
    """Test the driver raises exception on unsuccessful connection.

    Assert an authentication exception is raised if the database credentials
    are invalid.

    """
    current_app.config['GRAPHDB'] = CIGraphCreds
    current_app.config['GRAPHDB']['user'] = 'not a real user'
    current_app.config['GRAPHDB']['pass'] = 'foobar'
    with pytest.raises(neo4j.exceptions.AuthError):
        with Driver.session as session:
            session.run("MATCH (n) RETURN n LIMIT 1")


@pytest.mark.neo4
def test_driver_connection_cant_reach_server(client, Driver):
    """Test driver is not created if the server can't be reached.

    Assert an exception is raised if the driver can't reach the server.

    """
    current_app.config['GRAPHDB']['uri'] = 'bolt://foobar:1'
    with pytest.raises(neo4j.exceptions.AddressError):
        assert Driver.driver


@pytest.mark.neo4j
def test_driver_can_create_a_session(client, Driver, CIGraphCreds):
    """Test that a bound driver can create a session.

    Assert that a successfully connected driver is able to create a new
    session.

    """
    current_app.config['GRAPHDB'] = CIGraphCreds
    session = Driver.session
    assert isinstance(session, neo4j.v1.session.BoltSession)


@pytest.mark.neo4j
def test_driver_can_execute_cypher(client, Driver, CIGraphCreds):
    """Test that a bound driver can execute cypher.

    Assert that a successfully connected driver can execute cypher.

    """
    current_app.config['GRAPHDB'] = CIGraphCreds
    with Driver.session as session:
        session.run("MERGE (node:TestNode { name: $name, p1: $prop })",
                    name="CI Test", prop="Foobar")

    with Driver.session as session:
        result  = session.run("""MATCH (node)
                                 WHERE node.name = "CI Test"
                                 RETURN node.p1, node.name
                              """)
        assert result
        for record in result:
            assert record['node.name'] == "CI Test"
