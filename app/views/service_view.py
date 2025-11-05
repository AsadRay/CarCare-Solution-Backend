from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.service_controller import ServiceController
from app.models.user import User
from flask import Blueprint

service_bp = Blueprint('service', __name__)


def require_admin():
    """Decorator to check if user is admin"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None

@service_bp.route('/', methods=['GET'])
def get_services():
    """Get all services"""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    result, status_code = ServiceController.get_all_services(active_only)
    return jsonify(result), status_code

@service_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Get service by ID"""
    result, status_code = ServiceController.get_service_by_id(service_id)
    return jsonify(result), status_code

@service_bp.route('/category/<string:category>', methods=['GET'])
def get_services_by_category(category):
    """Get services by category"""
    result, status_code = ServiceController.get_services_by_category(category)
    return jsonify(result), status_code

@service_bp.route('/', methods=['POST'])
@jwt_required()
def create_service():
    """Create new service (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    result, status_code = ServiceController.create_service(data)
    return jsonify(result), status_code

@service_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """Update service (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    result, status_code = ServiceController.update_service(service_id, data)
    return jsonify(result), status_code

@service_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    """Delete service (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    result, status_code = ServiceController.delete_service(service_id)
    return jsonify(result), status_code