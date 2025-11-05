import os
from app import create_app
from flask_socketio import SocketIO



app = create_app()

socketio = SocketIO(app)

if __name__ == '__main__':
    # Run the app with WebSocket support
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )