"""Neo4j Driver Model.

This module defines the Node and Relationship models that can be used as a type
of ORM for Neo4j.

"""
import logging
import neo4j.exceptions
from flask import abort
from .exceptions import CypherError, NodeNotFound
from .validator import Validator, Integer


logger = logging.getLogger(__name__)



class Query(object):
    """Query Class.

    The query class is the core query component of the Node.

    """
    db = None

    def find_or_404(self, **kwargs):
        """Find nodes or 404.

        Wrapper around `find()` to search for records or abort 404 if no
        records are found.

        """
        try:
            return self.find(**kwargs)
        except NodeNotFound:
            abort(404, 'No nodes found')

    def find(self, label=None, limit=None, validate=False):
        """Find nodes

        Return all nodes from the database up to `limit`.

        Args:
            :param limit: Integer amount of nodes to limit. The default limit
                is 25.

        Returns:
            :return: List of Node objects or an empty list.

        """
        data = []
        records = None
        query = 'MATCH (node)\n'
        if label:
            query += 'WHERE node:{}\n'.format(label)
        query += 'RETURN node\n'
        if limit:
            query += 'LIMIT {}'.format(limit)

        logger.debug('Query: {}'.format(query))
        try:
            with Query.db.session as session:
                records = session.run(query)
        except neo4j.exceptions.CypherSyntaxError as ex:
            raise CypherError(ex)

        if not records.peek():  # if no records were returned
            raise NodeNotFound('No nodes where found')

        for record in records:
            node = Node.node_by_label(record["node"].labels.pop())()
            node.id = record["node"].id
            if validate:  # enforce validators; exception if fails
                for prop, value in record["node"].properties.items():
                    node.__setattr__(prop, value)
            else:  # bypass validation; load all properties as node props
                # need to use update() because we can't assign to __dict__
                node.__dict__.update(record["node"].properties)
            data.append(node)
        return data


def validate(cls):
    """Class decorator to support type validation.

    This decorator preforms two operations.

    * Iterate over class attributes and look for :class:`Validator` types to
    assign the instances `name` attribute.
    * Add discovered :class:`Validator` attributes to a list of acceptable
    attributes that can be set.

    """
    cls._attributes = {'id'}  # Set of allowed attributes
    for key, value in vars(cls).items():
        if isinstance(value, Validator):
            value.name = key  # Assign validator.name
            cls._attributes.add(key)  # add validator.name to acceptable attrs.
    return cls


class ResourceMeta(type):
    """Resource Meta class.

    This metaclass is used as the metaclass for the base types :class:`Node`
    and :class:`Relationship`.  Its purpose is to ensure that those base
    classes and their children are wrapped with the `@validate` class wrapper.

    """
    def __new__(meta, name, bases, methods):
        cls = super().__new__(meta, name, bases, methods)
        cls = validate(cls)  # wrap the class with @validate
        return cls


class Node(metaclass=ResourceMeta):
    """Node base class.

    This is the base class for Node models.  This class should be used to model
    your applications nodes within the neo4j graph database.

    This class should be inherited from in your applications models::

        from flask_neo4j.model import Neo4jDriver

        db = Neo4jDriver()

        class MyNode(db.Node):
            ... # Attributes / Validators

    The base node class provides a :class:`Query` object used to assist with
    the interaction of nodes and relationships within the graph database.  It
    is possible to overwrite the `Query` object by updating the `query`
    attribute with an alternative class.
    """
    query = Query()
    id = Integer(positive=True)

    def __setattr__(self, name, value):
        """Intercept setattr.

        Ensure that only attributes that have been defined can be set.

        """
        if name not in self._attributes:
            raise AttributeError(
                '{} has not defined attribute {}'.format(
                    self.__class__.__name__, name))
        super().__setattr__(name, value)

    @classmethod
    def node_by_label(cls, label):
        """Return a type of node based on `label`.

        Return a child of :class:`Node` that matches `label` if it exists;
        otherwise, return the base class.

        """
        models = {k.__name__: k for k in cls.__subclasses__()}
        if label in models:
            return models[label]
        return Node

    def save(self, merge=True, properties=None):
        """Commit model to the database.

        Serialize the model to the graph database.

        """
        with Node.query.db.session as session:
            if not properties:
                properties = self.__dict__
            label = self.__class__.__name__
            query = """MERGE (a:{label} {{ uid: $uid }})
                       SET a += $properties
                    """.format(label=label)
            logger.debug('Query: {}'.format(query))
            session.run(query, uid=self.uid, properties=properties)
