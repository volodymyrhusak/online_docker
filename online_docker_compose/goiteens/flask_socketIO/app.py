from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True


socketio = SocketIO(app)
socketio.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    session['name'] = 'test name'
    session['room'] = 'test room'
    name = session.get('name', '')
    room = session.get('room', '')
    if not (name or room):
        return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room)


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    print(session.get('name'))
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    print(session.get('name'))
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app)