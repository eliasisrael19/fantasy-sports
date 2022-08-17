import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app. The __name__ is finding where the Python module is located. 
    # instance_relative_config=True tells the app that configuration files are relative to instance foder. Can hold local data .
    app = Flask(__name__, instance_relative_config=True)

    # SECRET_KEY is ssed to keep data safe, and the DATABASE is the path where the SQLite database will be saved. 
    # its under app.instance_path since that is what Flask has chosen as Instance folder
    app.config['SECRET_KEY'] = 'dev'
    app.config['DATABASE'] = os.path.join(app.instance_path, 'Fantasyproject.sqlite') #initializing the database
    app.config['APP'] = 'Fantasyproject' #initializing the fantasy project
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True #better error messages in the future 

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists --> Flask does not create the instance folder automatically but needs to be created to create the SQLite Databas there.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello --> it creates connected between "/" and the inputed .html file.
    @app.route('/')
    def hello():
        return 'Hello World!'
    
    from.import db
    db.init_app(app) #once #init-db has been registered in app (look at db.py - REGISTER WITH THE APPLICATION) it can be used using the flask command.
#the function above will allow us to run the init-db in the command line- https://stackoverflow.com/questions/50158459/flask-tutorial-attributeerror-teardown-appcontext 

    from.import auth
    app.register_blueprint(auth.bp)
#Import and register the blueprint function and call the auth function. 
# USING THE ABOVE FUNCTION WE CAN HAVE REGISTER OF NEW USERS THAT COME IN AND OUT OF THE URL 

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    #Used to bring in the blog blueprint.

    return app
