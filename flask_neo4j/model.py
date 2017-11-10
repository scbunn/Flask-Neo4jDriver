"""Neo4j Driver Model.

This module contains the classes and functions that make up the
Flask-Neo4jDriver model system.

"""
import logging
import neo4j.exceptions
from flask import abort
from .exceptions import CypherError, NodeNotFound
from .validator import Validator, Integer, UUID


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

    The :class:`Node` maps class :class:`Property` objects to neo4j properties.
    Properties are stored as class attributes and their primary purpose is to
    preform validation on input values; however, not all properties preform
    input validation -- such as the :class:`UUID` property.

    There are a few default properties that exist on the base node.

    Default Properties:

        `query`: An instance of a :class:`Query` object.  The query instance
            can be replaced with a child of :class:`Query`.
        `id`: An instance of a :class:`Integer` property.  This id matches the
            id from a node in the graph database. It is *not* safe to use this
            value in your application.
        `uid`: An instance of a :class:`UUID` property.  This is the unique
            id that is assigned to the node and used internally by the model
            system.  It is safe to use this value in your application.

    In addition to the default properties, there are some instance level
    attributes that control aspects of the operation of the :class:`Node`.  In
    most cases, the defaults are fine.

    Default Attributes:

        `_CYPHER_ON_CREATE`: This attribute is used to set properties on nodes
            when using a `MERGE` operation and the node does not exist.
        `_CYPHER_ON_MATCH`: This attribute is used to set properties on nodes
            when using a `MERGE` operation and the node already exists.

        Example::

            MyNode(Node):
                def __init__(self):
                    super().__init__()
                    self._CYPHER_ON_MATCH = "node.updated = timestamp()"
                    self._CYPHER_ON_CREATE = "node.created = timestamp()"

        This would result in the following cypher query being executed when the
        node commits its data to the database::

            MERGE (node:Node {uid: 123})
            ON CREATE SET node.created = timestamp()
            ON MATCH SET node.updated = timestamp()
            RETURN node

        When a :class:`Node` commits data, it always uses `node` as the
        identifier. `ON_CREATE` and `ON_MATCH` can be a comma delimited list.

    """
    query = Query()
    id = Integer(positive=True)  # Id from the graph db
    uid = UUID()                 # internal tracking id

    def __init__(self):
        """Base node initialization.

        Initialize a base node.  Here we set some default attributes of all
        children.

        """

        # Add some attributes that are outside of normal operations
        # If the attribute is not part of this set, the class will reject
        # its assignment
        self._attributes.update({
            '_CYPHER_ON_CREATE',   # Used for MERGE ... ON CREATE
            '_CYPHER_ON_MATCH',    # Used for MERGE ... ON MATCH
            '_LABEL'               # Used to overwrite label of node
        })

    def __setattr__(self, name, value):
        """Intercept setattr.

        Ensure that only attributes that have been defined can be set.

        """
        if name not in self._attributes:
            raise AttributeError(
                '{} has not defined attribute {}'.format(
                    self.__class__.__name__, name))
        super().__setattr__(name, value)

    def __str__(self):
        return '<{}: {}>'.format(self.label, self.uid)

    def __repr__(self):
        return '<{}: {}; {}>'.format(self.label, self.uid, self.properties)

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

    @classmethod
    def from_dict(cls, data):
        """Construct a new :class:`Node` from a dictionary.

        Constructs a new node from the passed dictionary. The type of node
        created is based on the name of the invoking class or `_LABEL`.

        """
        if not isinstance(data, dict):
            raise TypeError('from_dict requires a dictionary')

        if hasattr(cls, "_LABEL"):
            label = cls._LABEL
        else:
            label = cls.__name__
        print(f'looking for a class with label: {label}')
        node = Node.node_by_label(label)()
        node.__dict__.update(data)
        return node

    def to_dict(self):
        """Return a dictionary structure representing this model.

        Returns a dictionary representation of the object.  If the caller is
        returning a `JSON` object and wants to filter the properties returned,
        then override this method.

        """
        self.uid  # ensure the uid is set
        return {self.label: self.properties}

    @property
    def label(self):
        """Return the label to use for the node.

        The default is to return the name of the class.  This can be
        overwritten by assigning a value to `_LABEL`

        """
        if hasattr(self, '_LABEL'):
            return self._LABEL
        return self.__class__.__name__

    @property
    def properties(self):
        """Return a dict of properties.

        Returns a dictionary of properties that can be saved to the graph db.

        """
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith('_') and k != 'id'}

    def _merge_node(self):
        """Commit model to the database by merge.

        Serialize this model to the database using a `MERGE` operation.

        """
        logger.debug("Merging model to the database: {}".format(self))

        # Base query
        query = [
            "MERGE (node:{label} {{uid: $uid}})".format(label=self.label),
            "SET node += $properties",
        ]

        # Add ON_CREATE/ON_MATCH if requested
        if hasattr(self, "_CYPHER_ON_CREATE"):
            query.insert(1, "ON CREATE SET {}".format(self._CYPHER_ON_CREATE))
        if hasattr(self, "_CYPHER_ON_MATCH"):
            query.insert(1, "ON MATCH SET {}".format(self._CYPHER_ON_MATCH))

        # Serialize the model
        logger.debug("Merge Query: {}".format('\n'.join(query)))
        with self.query.db.session as tx:
            tx.run('\n'.join(query), uid=self.uid, properties=self.properties)

    def _create_node(self):
        """Commit model to the database by create.

        Serialize this model to the database using a `CREATE` operation.

        """
        logger.debug("Create new node: {}".format(self))
        query = "CREATE (node:{label} $properties)".format(label=self.label)
        with self.query.db.session as tx:
            logger.debug("Create query: {}".format(query))
            tx.run(query, properties=self.properties)

    def save(self, merge=True):
        """Commit model to the database.

        Serialize the model to the graph database.

        Args:
            :param merge: flag to determine if save should merge or create

        Raises:
            neo4j.exceptions.ConstraintError: if a constraint is violated.
            neo4j.exceptions.CypherSyntaxError: if cypher breaks.

        """
        if merge:
            self._merge_node()
        else:
            self._create_node()
