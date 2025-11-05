from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.vehicle_controller import VehicleController

vehicle_bp = Blueprint('vehicle', __name__)

@vehicle_bp.route('/', methods=['POST'])
@jwt_required()
def create_vehicle():
    """Create a new vehicle"""
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status_code = VehicleController.create_vehicle(user_id, data)
    return jsonify(result), status_code

@vehicle_bp.route('/', methods=['GET'])
@jwt_required()
def get_vehicles():
    """Get all vehicles for current user"""
    user_id = get_jwt_identity()
    result, status_code = VehicleController.get_user_vehicles(user_id)
    return jsonify(result), status_code

@vehicle_bp.route('/<int:vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicle(vehicle_id):
    """Get specific vehicle by ID"""
    user_id = get_jwt_identity()
    result, status_code = VehicleController.get_vehicle_by_id(vehicle_id, user_id)
    return jsonify(result), status_code

@vehicle_bp.route('/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update vehicle information"""
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status_code = VehicleController.update_vehicle(vehicle_id, user_id, data)
    return jsonify(result), status_code

@vehicle_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    user_id = get_jwt_identity()
    result, status_code = VehicleController.delete_vehicle(vehicle_id, user_id)
    return jsonify(result), status_code

@vehicle_bp.route('/<int:vehicle_id>/appointments', methods=['GET'])
@jwt_required()
def get_vehicle_appointments(vehicle_id):
    """Get all appointments for a vehicle"""
    user_id = get_jwt_identity()
    result, status_code = VehicleController.get_vehicle_appointments(vehicle_id, user_id)
    return jsonify(result), status_code