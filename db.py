#FIRST PART IS USED TO CONNECT TO DATABASE

import sqlite3

import click
#g is used to store data in each request 
#current_app called in order to handle the request.
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
    # sqlite3.connect() establish a connection to the file "Database"
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        #sqlite3.Row returns rows
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()





#### This is the second part of the db.py and the Python function below will run the SQL commands from the schema.sql file when we created the tables (empty tables)
def init_db():
    db = get_db()
    #get_db will return a database connection

    #open_resource() opens a file relative to the Fantasyproject package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


#click.command defines a command line command called init-db and calls the init_db function. It shows a message of "sucess" to user. This is to say "it worked!"
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')




###### REGISTER WITH THE APPLICATION SECtion (https://flask.palletsprojects.com/en/2.1.x/tutorial/database/)##########
# close_db and init_db_command functions will need to be registered with the application instance.
# otherwise wont be used by the application
def init_app(app):
    app.teardown_appcontext(close_db)
    #app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.

    app.cli.add_command(init_db_command)
    #app.cli.add_command() adds a new command that can be called with the flask command.