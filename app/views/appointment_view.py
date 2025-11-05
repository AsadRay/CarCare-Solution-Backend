from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.appointment_controller import AppointmentController
from app.models.user import User
from flask import Blueprint

appointment_bp = Blueprint('appointment', __name__)


def get_current_user():
    """Helper to get current user"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@appointment_bp.route('/', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment"""
    customer_id = get_jwt_identity()
    data = request.get_json()
    result, status_code = AppointmentController.create_appointment(customer_id, data)
    return jsonify(result), status_code

@appointment_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get user appointments"""
    user = get_current_user()
    filters = {
        'status': request.args.get('status'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date')
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    result, status_code = AppointmentController.get_appointments(user.id, user.role, filters)
    return jsonify(result), status_code

@appointment_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get single appointment by ID"""
    user = get_current_user()
    result, status_code = AppointmentController.get_appointment_by_id(
        appointment_id, user.id, user.role
    )
    return jsonify(result), status_code

@appointment_bp.route('/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment"""
    user = get_current_user()
    data = request.get_json()
    result, status_code = AppointmentController.update_appointment(
        appointment_id, user.id, user.role, data
    )
    return jsonify(result), status_code

@appointment_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel appointment"""
    user = get_current_user()
    data = request.get_json() or {}
    reason = data.get('reason', '')
    result, status_code = AppointmentController.cancel_appointment(
        appointment_id, user.id, user.role, reason
    )
    return jsonify(result), status_code

@appointment_bp.route('/available-slots', methods=['GET'])
def get_available_slots():
    """Get available time slots for booking"""
    service_id = request.args.get('service_id', type=int)
    date = request.args.get('date')
    provider_id = request.args.get('provider_id', type=int)
    
    if not service_id or not date:
        return jsonify({'error': 'service_id and date are required'}), 400
    
    result, status_code = AppointmentController.get_available_slots(
        service_id, date, provider_id
    )
    return jsonify(result), status_code