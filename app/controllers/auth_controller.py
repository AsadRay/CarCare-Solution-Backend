from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token
from app.utils.validators import validate_email, validate_password

class AuthController:
    
    @staticmethod
    def register(data):
        try:
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            phone = data.get('phone', '').strip()
            role = data.get('role', 'customer')
            
            if not all([email, password, first_name, last_name]):
                return {'error': 'Missing required fields'}, 400
            
            if not validate_email(email):
                return {'error': 'Invalid email format'}, 400
            
            password_valid, password_msg = validate_password(password)
            if not password_valid:
                return {'error': password_msg}, 400
            
            if User.query.filter_by(email=email).first():
                return {'error': 'Email already registered'}, 409
            
            if role not in ['customer', 'provider', 'admin']:
                return {'error': 'Invalid role'}, 400
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'message': 'User registered successfully',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Registration failed: {str(e)}'}, 500
    
    @staticmethod
    def login(data):
        try:
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return {'error': 'Email and password required'}, 400
            
            # Find user
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return {'error': 'Invalid credentials'}, 401
            
            if not user.is_active:
                return {'error': 'Account is deactivated'}, 403
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
            
        except Exception as e:
            return {'error': f'Login failed: {str(e)}'}, 500
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile by ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            return {'user': user.to_dict()}, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch profile: {str(e)}'}, 500
    
    @staticmethod
    def update_profile(user_id, data):
        """Update user profile"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            if 'first_name' in data:
                user.first_name = data['first_name'].strip()
            if 'last_name' in data:
                user.last_name = data['last_name'].strip()
            if 'phone' in data:
                user.phone = data['phone'].strip()
            
            db.session.commit()
            
            return {
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Update failed: {str(e)}'}, 500
        
