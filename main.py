from flask import Flask, render_template, request, redirect, url_for
import socket
import json
from datetime import datetime

app = Flask(__name__)


# Socket server thread function
def socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('127.0.0.1', 5000))

    while True:
        data, addr = server.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        message['timestamp'] = timestamp

        with open('storage/data.json', 'r+') as file:
            data = json.load(file)
            data[timestamp] = message
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()


# Start socket server in a separate thread
import threading

socket_thread = threading.Thread(target=socket_server)
socket_thread.start()


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message')
def message():
    return render_template('message.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    username = request.form.get('username')
    message_text = request.form.get('message')

    message = {
        'username': username,
        'message': message_text
    }

    # Send message to socket server
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(message).encode('utf-8'), ('127.0.0.1', 5000))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False, port=3000)
