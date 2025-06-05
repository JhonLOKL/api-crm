from flask import Flask, request

from flask_cors import CORS

from src.services.leadCRM import lead_crm
from src.services.bedroomSerices import bedroomDummies
from src.services.hotelServices import hotelDummies
from services.registersDB import save_register_in_db
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

@app.route("/lead", methods=["POST"])
def add_lead():

    data = request.get_json()
    
    return lead_crm(data), 201

@app.route("/register", methods=["POST"])
def add_register():

    data = request.get_json()
    
    if( not ('email' in data or 'phone' in data) ):
        return "Es necesario un correo o un telefono", 400
    
    return save_register(data), 201

@app.route("/dbregister", methods=["POST"])
def add_register_in_db():
    data = request.get_json()
    return save_register_in_db(data), 201

@app.route("/hotel/dummies", methods=["post"])
def hotelDummiesProcess():
    return hotelDummies()

@app.route("/bedroom/dummies", methods=["post"])
def bedroomDummiesProcess():
    return bedroomDummies()

if __name__ == '__main__':
    app.run(debug=True)

