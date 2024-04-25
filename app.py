"""
    Simple web app to try the Flask framwork
"""

# IMPORTS =====================================================
from flask import Flask

from routes.user import user_blueprint
from database.db import init_db


# INSTANCE OF THE APP WITH FLASK =============================
app = Flask(__name__)


# REGISTER OF THE BLUEPRINT ==================================
app.register_blueprint(user_blueprint, url_prefix='/api')


# MONGO DB CONFIGURATION =====================================
# 'mongo-db' is the service name in docker compose
app.config['MONGO_URI'] = 'mongodb://mongo-db:27017/mydatabase'
init_db(app)  # Initialize MongoDB with the current Flask app


# ========= ROUTES ===========================================
@app.route('/')
def health_check():
    """ Health check just that """
    return 'Service up and running!'
