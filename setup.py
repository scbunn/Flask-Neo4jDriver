"""
Flask-Neo4J-Driver
------------------

Flask extension providing integration with the official Neo4j python driver.

"""
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask-Neo4jDriver',
    version='0.2.0',
    url='https://github.com/scbunn/flask-neo4jdriver',
    license='GPLv3',
    author='Stephen Bunn',
    author_email='scbunn@sbunn.org',
    description='Flask extension for official neo4j python driver.',
    long_description=read('README.rst'),
    packages=['flask_neo4j'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'neo4j-driver'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-spec',
        'pytest-flask',
        'Faker'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='flask neo4j database graph',
    python_requires='>=3',
)
