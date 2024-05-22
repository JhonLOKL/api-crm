import datetime
from flask import Flask, json, jsonify, request
import src.services.connectCRM as connection
from decouple import config

app = Flask(__name__)

@app.route("/")
def root():
    return  config('SECRET_KEY')

@app.route("/simulation", methods=["POST"])
def add_simulation():

    data = request.get_json()
    
    if( not ('email' in data or 'phone' in data) ):
        return "Es necesario un correo o un telefono", 400
    
    return connection.save_simulation(data), 201

if __name__ == '__main__':
    app.run(debug=True)

