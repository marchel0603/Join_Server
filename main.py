from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

rooms = {}  # Dictionary to store room information

def generate_pin():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    pin = generate_pin()
    rooms[pin] = []
    session['room'] = pin
    return redirect(url_for('room', pin=pin))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        pin = request.form.get('pin')
        if pin in rooms:
            session['room'] = pin
            return redirect(url_for('room', pin=pin))
        else:
            return render_template('join.html', error="Invalid PIN")
    return render_template('join.html')

@app.route('/room/<pin>')
def room(pin):
    if 'room' not in session or session['room'] != pin:
        return redirect(url_for('index'))
    return render_template('room.html', pin=pin)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'msg': f'{username} has joined the room.'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    emit('message', {'msg': msg}, room=room)

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    socketio.run(app, host='0.0.0.0', port=5000)
