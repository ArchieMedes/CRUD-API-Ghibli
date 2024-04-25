"""
    Here we initialize the mongodb
    to be accessed at any point of the app
"""

# IMPORTS =========================================
from flask_pymongo import PyMongo


# SETTING =========================================
mongo = PyMongo()


# INITIALIZE THE DB ===============================
def init_db(app):
    """
        here we initialize mongodb with the current flask app

        we do this just one time at the beginning of the runtime
        of the "app.py" file, but this makes the database callable
        from any other point of our application
    """
    mongo.init_app(app)
