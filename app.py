from flask import Flask
from database import initialise_database

from routes.auth_routes import auth
from routes.main_routes import main

app=Flask(__name__)

app.config["SECRET_KEY"]="random_secret_key"

app.register_blueprint(auth)
app.register_blueprint(main)

initialise_database()

if __name__=="__main__":
    app.run(debug=True)