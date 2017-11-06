Flask-Neo4jDriver
=================

Flask-Neo4jDriver is a flask extension that provides integration with the 
official neo4j python drivers.

Flask-Neo4jDriver > 0.2.0 requires `python 3`_.  Experimental graph mapping
models are introduced in version 0.2.0.

.. _python 3: https://docs.python.org/3/

Introduction
------------

This extension provides basic integration with the official `python driver`_.

Flask-Neo4jDriver is designed to provide an interface to the `Neo4j`_ graph 
database.  This extension exposes the `neo4j.v1.GraphDatabase.Driver` 
object for direct manipulation.

Additionally, this extension provides a handful of helper utility methods
including the following:

* `session`.  Return a `GraphDatabase.Session`
* `query()`.  Run a cypher query within a `session()` context.

.. _python driver: https://github.com/neo4j/neo4j-python-driverk
.. _Neo4j: https://neo4j.com


Installation
------------

Flask-Neo4jDriver can be installed from PyPI.

.. code:: bash

   pip install Flask-Neo4jDriver

To install the latest development version, use:

.. code:: bash

   pip install git+https://github.com/scbunn/flask-neo4jdriver.git@develop


Usage
-----

In order to use this extension you need to initialize it with the flask
application.  This can be done directly or via an application factory.  Once
the extension has been initialized it is available through the `db` object.

Configuration
~~~~~~~~~~~~~

Flask-Neo4jDriver supports the following configuration options.

+-------------------+-------------------------------------+-----------------------+
| Configuration Key | Description                         | Default               |
+===================+=====================================+=======================+
| GRAPHDB_URI       | URI of the Neo4j Database           | bolt://localhost:7687 |
+-------------------+-------------------------------------+-----------------------+
| GRAPHDB_USER      | Username to connect to the database | neo4j                 |
+-------------------+-------------------------------------+-----------------------+
| GRAPHDB_PASS      | Password for the user               | neo4j                 |
+-------------------+-------------------------------------+-----------------------+

Example:

.. code-block:: python

   import os
   from flask import Flask
   from flask.ext.neo4jdriver import Neo4jDriver

   app = Flask(__name__)
   app.config['GRAPHDB_URI'] = 'bolt://neo4j.host:7687'
   app.config['GRAPHDB_USER'] = 'appuser'
   app.config['GRAPHDB_PASS'] = os.getenv('GRAPHDB_PASS', '')

   db = Neo4jDriver(app)


Direct Initialization
~~~~~~~~~~~~~~~~~~~~~

If you are not using an application factory, then you can initialize this
extension directly.

.. code-block:: python

   from flask import Flask
   from flask.ext.neo4jdriver import Neo4jDriver

   app = Flask(__name__)
   db = Neo4jDriver(app)

Application Factories
~~~~~~~~~~~~~~~~~~~~~

If you are using an application factory, then you can initialize this 
extension within your `create_app()` method.

in models.py

.. code-block:: python

   from flask.ext.neo4jdriver import Neo4jDriver

   db = Neo4jDriver()

At your application factory

.. code-block:: python

   from flask import Flask


   def create_app(config_filename):
       app = Flask(__name__)
       app.config.from_pyfile(config_filename)

       from yourapplication.models import db
       db.init_app(app)

Testing
-------

You can execute the test suite using setup.py

.. code:: bash

   python setup.py test


Contributing
------------

Have features you want to add? Fork this repository and send me a pull 
request.  Please make sure you include test cases for any additional features.
