from flask_socketio import emit, join_room, leave_room
from app import socketio

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('join_provider_room')
def handle_join_provider_room(data):
    """Provider joins their room to receive booking updates"""
    provider_id = data.get('provider_id')
    if provider_id:
        room = f'provider_{provider_id}'
        join_room(room)
        emit('room_joined', {'room': room})

@socketio.on('leave_provider_room')
def handle_leave_provider_room(data):
    """Provider leaves their room"""
    provider_id = data.get('provider_id')
    if provider_id:
        room = f'provider_{provider_id}'
        leave_room(room)
        emit('room_left', {'room': room})

def notify_new_appointment(provider_id, appointment_data):
    """Notify provider of new appointment"""
    if provider_id:
        room = f'provider_{provider_id}'
        socketio.emit('new_appointment', appointment_data, room=room)

def notify_appointment_cancelled(provider_id, appointment_data):
    """Notify provider of cancelled appointment"""
    if provider_id:
        room = f'provider_{provider_id}'
        socketio.emit('appointment_cancelled', appointment_data, room=room)

def broadcast_slot_update(service_id, date):
    """Broadcast that slots have been updated"""
    socketio.emit('slots_updated', {
        'service_id': service_id,
        'date': date
    }, broadcast=True)