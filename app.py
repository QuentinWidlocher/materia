from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin
import controller as ctrl

app = Flask(__name__, 
            static_folder = "./dist/static",
            template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app)

json = {"content-type": "application/json"}

##
### API
##

# Get all users
@app.route('/api/users/', methods=['GET'])
@app.route('/api/users', methods=['GET'])
@cross_origin()
def get_all_users():
    return ctrl.get_all_users(), json

# Get a user
@app.route('/api/users/<id>/', methods=['GET'])
@app.route('/api/users/<id>', methods=['GET'])
@cross_origin()
def get_user(id):
    return ctrl.get_user(id), json

# Try to login
@app.route('/api/users/login/', methods=['POST'])
@app.route('/api/users/login', methods=['POST'])
@cross_origin()
def login():
    return ctrl.login(request.get_json()), json

# Get the first message of a conversation
@app.route('/api/messages/<id_from>/<id_to>/last/', methods=['GET'])
@app.route('/api/messages/<id_from>/<id_to>/last', methods=['GET'])
@cross_origin()
def get_last_message(id_from, id_to):
    return ctrl.get_last_message(id_from, id_to), json
    
# Get all messages FROM id_from TO id_to
@app.route('/api/messages/<id_from>/<id_to>/', methods=['GET'])
@app.route('/api/messages/<id_from>/<id_to>', methods=['GET'])
@cross_origin()
def get_messages(id_from, id_to):
    return ctrl.get_messages(id_from, id_to), json



##
### INTERFACE
##

# All other path lead to index.html (VueJS)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


##
### SOCKET IO
##

# On client connecting
@socketio.on('connect')
def connect():
    emit('welcome')

# On message sent
@socketio.on('message')
def message(message):

    # We add the message to the DB
    ctrl.add_message(message)

    # We transmit the message to everyone else
    # TODO: use a room system to transmit only to concerned people
    emit('message', message, broadcast=True, include_self=False)

if __name__ == '__main__':
    
    # We initialize the Firebase DB first
    ctrl.init()

    socketio.run(app, host='0.0.0.0', port=5000)