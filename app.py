from flask import Flask, request

from flask_cors import CORS

from src.services.registersCRM import save_register
from src.services.simulationsCRM import save_simulation

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def root():
    return  "Conectado!"

@app.route("/simulation", methods=["POST"])
def add_simulation():

    data = request.get_json()
    
    if( not ('email' in data or 'phone' in data) ):
        return "Es necesario un correo o un telefono", 400
    
    return save_simulation(data), 201

@app.route("/register", methods=["POST"])
def add_register():

    data = request.get_json()
    
    if( not ('email' in data or 'phone' in data) ):
        return "Es necesario un correo o un telefono", 400
    
    return save_register(data), 201

if __name__ == '__main__':
    app.run(debug=True)

