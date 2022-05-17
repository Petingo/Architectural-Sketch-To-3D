import json
from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__,
            static_url_path="/",
            static_folder="web/static",
            template_folder="web/templates")

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on('new_path')
def handle_new_path(json_data):
    data = json.loads(str(json_data))
    print(data)

if __name__ == '__main__':
    socketio.run(app)