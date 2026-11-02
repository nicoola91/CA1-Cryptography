from flask import Flask
from database import initialize_database

app=Flask(__name__)

app.config["SECRET_KEY"]="random_secret_key"

initialize_database()

if __name__=="__main__":
    app.run(debug=True)