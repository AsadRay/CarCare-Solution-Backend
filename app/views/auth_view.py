from flask import request, jsonify, session, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.auth_controller import AuthController
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    result, status_code = AuthController.register(data)
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    result, status_code = AuthController.login(data)
    return jsonify(result), status_code

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    result, status_code = AuthController.get_user_profile(user_id)
    return jsonify(result), status_code

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status_code = AuthController.update_profile(user_id, data)
    return jsonify(result), status_code

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    session.pop(user_id, None)
    return jsonify({'message': 'Logout successful'}), 200