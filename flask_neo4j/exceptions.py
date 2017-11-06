"""Flask Neo4jDriver Exceptions.

This module defines the exceptions used by the Neo4jDriver Flask extension.

Several of the neo4j-driver exceptions are subclassed here.  This is to assist
the caller in dealing with exceptions without having to have intimate knowledge
of the neo4j-driver.

If the caller is using the neo4j driver directly, then the caller will be
responsible for dealing with neo4j-driver exceptions directly.

"""
import neo4j.exceptions


class CypherError(neo4j.exceptions.CypherError):
    pass

class NodeNotFound(Exception):

    def __init__(self, message, status_code=404, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload
