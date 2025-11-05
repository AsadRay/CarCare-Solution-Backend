from app import db
from app.models.user import User
from app.models.availability import Availability
from datetime import time

class ProviderController:
    
    @staticmethod
    def get_all_providers():
        """Get all active providers"""
        try:
            providers = User.query.filter_by(
                role='provider',
                is_active=True
            ).all()
            
            return {
                'providers': [provider.to_dict() for provider in providers]
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch providers: {str(e)}'}, 500
    
    @staticmethod
    def get_provider_by_id(provider_id):
        """Get provider details"""
        try:
            provider = User.query.filter_by(
                id=provider_id,
                role='provider'
            ).first()
            
            if not provider:
                return {'error': 'Provider not found'}, 404
            
            # Include availability
            availability = Availability.query.filter_by(
                provider_id=provider_id
            ).all()
            
            provider_data = provider.to_dict()
            provider_data['availability'] = [avail.to_dict() for avail in availability]
            
            return {'provider': provider_data}, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch provider: {str(e)}'}, 500
    
    @staticmethod
    def set_availability(provider_id, data):
        """Set provider availability schedule"""
        try:
            provider = User.query.filter_by(
                id=provider_id,
                role='provider'
            ).first()
            
            if not provider:
                return {'error': 'Provider not found'}, 404
            
            day_of_week = data.get('day_of_week')
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            is_available = data.get('is_available', True)
            
            # Validation
            if day_of_week is None or start_time_str is None or end_time_str is None:
                return {'error': 'Missing required fields'}, 400
            
            if not (0 <= day_of_week <= 6):
                return {'error': 'Invalid day_of_week (0-6)'}, 400
            
            # Parse times
            try:
                start_time = time.fromisoformat(start_time_str)
                end_time = time.fromisoformat(end_time_str)
            except ValueError:
                return {'error': 'Invalid time format. Use HH:MM:SS'}, 400
            
            if start_time >= end_time:
                return {'error': 'Start time must be before end time'}, 400
            
            # Check if availability exists for this day
            availability = Availability.query.filter_by(
                provider_id=provider_id,
                day_of_week=day_of_week
            ).first()
            
            if availability:
                # Update existing
                availability.start_time = start_time
                availability.end_time = end_time
                availability.is_available = is_available
            else:
                # Create new
                availability = Availability(
                    provider_id=provider_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=is_available
                )
                db.session.add(availability)
            
            db.session.commit()
            
            return {
                'message': 'Availability set successfully',
                'availability': availability.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to set availability: {str(e)}'}, 500
    
    @staticmethod
    def get_availability(provider_id):
        """Get provider availability schedule"""
        try:
            availability = Availability.query.filter_by(
                provider_id=provider_id
            ).order_by(Availability.day_of_week).all()
            
            return {
                'availability': [avail.to_dict() for avail in availability]
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch availability: {str(e)}'}, 500
    
    @staticmethod
    def delete_availability(provider_id, availability_id):
        """Delete availability slot"""
        try:
            availability = Availability.query.filter_by(
                id=availability_id,
                provider_id=provider_id
            ).first()
            
            if not availability:
                return {'error': 'Availability not found'}, 404
            
            db.session.delete(availability)
            db.session.commit()
            
            return {'message': 'Availability deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete availability: {str(e)}'}, 500