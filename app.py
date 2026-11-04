from flask import Flask
from database import initialise_database
from routes.file_routes import file_routes

from routes.auth_routes import auth
from routes.main_routes import main

app=Flask(__name__)

app.config["SECRET_KEY"]="random_secret_key"

app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(file_routes)

initialise_database()

if __name__=="__main__":
    app.run(debug=True)