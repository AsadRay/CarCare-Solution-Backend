from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.provider_controller import ProviderController
from app.models.user import User
from flask import Blueprint


provider_bp = Blueprint('provider', __name__)


@provider_bp.route('/', methods=['GET'])
def get_providers():
    """Get all active providers"""
    result, status_code = ProviderController.get_all_providers()
    return jsonify(result), status_code

@provider_bp.route('/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    """Get provider details"""
    result, status_code = ProviderController.get_provider_by_id(provider_id)
    return jsonify(result), status_code

@provider_bp.route('/<int:provider_id>/availability', methods=['GET'])
def get_availability(provider_id):
    """Get provider availability"""
    result, status_code = ProviderController.get_availability(provider_id)
    return jsonify(result), status_code

@provider_bp.route('/availability', methods=['POST'])
@jwt_required()
def set_availability():
    """Set provider availability (provider only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'provider':
        return jsonify({'error': 'Provider access required'}), 403
    
    data = request.get_json()
    result, status_code = ProviderController.set_availability(user_id, data)
    return jsonify(result), status_code

@provider_bp.route('/availability/<int:availability_id>', methods=['DELETE'])
@jwt_required()
def delete_availability(availability_id):
    """Delete availability slot (provider only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'provider':
        return jsonify({'error': 'Provider access required'}), 403
    
    result, status_code = ProviderController.delete_availability(user_id, availability_id)
    return jsonify(result), status_code