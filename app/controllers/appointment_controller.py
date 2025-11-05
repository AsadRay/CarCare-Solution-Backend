from app import db
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.vehicle import Vehicle
from app.models.user import User
from datetime import datetime, timedelta
from app.utils.validators import validate_time_slot
from app.utils.notifications import send_appointment_confirmation
from sqlalchemy import and_, or_
from config import Config


class AppointmentController:
    
    @staticmethod
    def create_appointment(customer_id, data):
        """Create a new appointment"""
        try:
            service_id = data.get('service_id')
            vehicle_id = data.get('vehicle_id')
            start_time_str = data.get('start_time')
            provider_id = data.get('provider_id')
            notes = data.get('notes', '')
            
            # Validate required fields
            if not all([service_id, vehicle_id, start_time_str]):
                return {'error': 'Missing required fields'}, 400
            
            # Parse start time
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            except ValueError:
                return {'error': 'Invalid start_time format. Use ISO format'}, 400
            
            # Validate service exists
            service = Service.query.get(service_id)
            if not service or not service.is_active:
                return {'error': 'Service not found or inactive'}, 404
            
            # Validate vehicle belongs to customer
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle or vehicle.user_id != customer_id:
                return {'error': 'Vehicle not found or does not belong to customer'}, 404
            
            # Calculate end time
            end_time = start_time + timedelta(minutes=service.duration_minutes)
            
            # Validate time slot
            slot_valid, slot_msg = validate_time_slot(start_time, end_time)
            if not slot_valid:
                return {'error': slot_msg}, 400
            
            # Check for conflicts with existing appointments
            conflict = AppointmentController._check_conflicts(
                provider_id, start_time, end_time
            )
            if conflict:
                return {'error': 'Time slot not available. Conflict with existing appointment'}, 409
            
            # Create appointment
            appointment = Appointment(
                customer_id=customer_id,
                provider_id=provider_id,
                service_id=service_id,
                vehicle_id=vehicle_id,
                start_time=start_time,
                end_time=end_time,
                status='pending',
                notes=notes
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            # Send confirmation notifications
            customer = User.query.get(customer_id)
            appointment_data = appointment.to_dict(include_relations=True)
            
            # Send email notification
            if customer and customer.email:
                send_appointment_confirmation(customer.email, appointment_data)
            
            # Send SMS notification
            if customer and customer.phone:
                from app.utils.notifications import send_appointment_sms
                send_appointment_sms(customer.phone, appointment_data)
            
            return {
                'message': 'Appointment created successfully',
                'appointment': appointment_data
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to create appointment: {str(e)}'}, 500
    
    @staticmethod
    def _check_conflicts(provider_id, start_time, end_time, exclude_id=None):
        """Check for appointment conflicts"""
        query = Appointment.query.filter(
            Appointment.status.in_(['pending', 'confirmed', 'in_progress']),
            or_(
                and_(Appointment.start_time <= start_time, Appointment.end_time > start_time),
                and_(Appointment.start_time < end_time, Appointment.end_time >= end_time),
                and_(Appointment.start_time >= start_time, Appointment.end_time <= end_time)
            )
        )
        
        if provider_id:
            query = query.filter(Appointment.provider_id == provider_id)
        
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
        
        return query.first() is not None
    
    @staticmethod
    def get_appointments(user_id, role, filters=None):
        """Get appointments based on user role"""
        try:
            query = Appointment.query
            
            if role == 'customer':
                query = query.filter_by(customer_id=user_id)
            elif role == 'provider':
                query = query.filter_by(provider_id=user_id)
            
            # Apply filters
            if filters:
                if 'status' in filters:
                    query = query.filter_by(status=filters['status'])
                if 'start_date' in filters:
                    start_date = datetime.fromisoformat(filters['start_date'])
                    query = query.filter(Appointment.start_time >= start_date)
                if 'end_date' in filters:
                    end_date = datetime.fromisoformat(filters['end_date'])
                    query = query.filter(Appointment.start_time <= end_date)
            
            appointments = query.order_by(Appointment.start_time.desc()).all()
            
            return {
                'appointments': [apt.to_dict(include_relations=True) for apt in appointments]
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch appointments: {str(e)}'}, 500
    
    @staticmethod
    def get_appointment_by_id(appointment_id, user_id, role):
        """Get single appointment by ID"""
        try:
            appointment = Appointment.query.get(appointment_id)
            
            if not appointment:
                return {'error': 'Appointment not found'}, 404
            
            # Authorization check
            if role == 'customer' and appointment.customer_id != user_id:
                return {'error': 'Unauthorized'}, 403
            elif role == 'provider' and appointment.provider_id != user_id:
                return {'error': 'Unauthorized'}, 403
            
            return {'appointment': appointment.to_dict(include_relations=True)}, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch appointment: {str(e)}'}, 500
    
    @staticmethod
    def update_appointment(appointment_id, user_id, role, data):
        """Update appointment"""
        try:
            appointment = Appointment.query.get(appointment_id)
            
            if not appointment:
                return {'error': 'Appointment not found'}, 404
            
            # Authorization
            if role == 'customer' and appointment.customer_id != user_id:
                return {'error': 'Unauthorized'}, 403
            
            # Customers can only cancel or update notes
            if role == 'customer':
                if 'status' in data and data['status'] == 'cancelled':
                    appointment.status = 'cancelled'
                    appointment.cancellation_reason = data.get('cancellation_reason', '')
                if 'notes' in data:
                    appointment.notes = data['notes']
            
            # Providers can update status and notes
            elif role == 'provider' and appointment.provider_id == user_id:
                if 'status' in data:
                    appointment.status = data['status']
                if 'notes' in data:
                    appointment.notes = data['notes']
            
            # Admins can update everything
            elif role == 'admin':
                for key, value in data.items():
                    if hasattr(appointment, key) and key not in ['id', 'created_at']:
                        setattr(appointment, key, value)
            else:
                return {'error': 'Unauthorized'}, 403
            
            db.session.commit()
            
            return {
                'message': 'Appointment updated successfully',
                'appointment': appointment.to_dict(include_relations=True)
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update appointment: {str(e)}'}, 500
    
    @staticmethod
    def cancel_appointment(appointment_id, user_id, role, reason=''):
        """Cancel an appointment"""
        try:
            appointment = Appointment.query.get(appointment_id)
            
            if not appointment:
                return {'error': 'Appointment not found'}, 404
            
            # Authorization
            if role == 'customer' and appointment.customer_id != user_id:
                return {'error': 'Unauthorized'}, 403
            elif role == 'provider' and appointment.provider_id != user_id:
                return {'error': 'Unauthorized'}, 403
            
            # Check if already cancelled
            if appointment.status == 'cancelled':
                return {'error': 'Appointment already cancelled'}, 400
            
            # Check cancellation window
            time_until = (appointment.start_time - datetime.utcnow()).total_seconds() / 3600
            
            if time_until < Config.CANCELLATION_WINDOW_HOURS and role == 'customer':
                return {
                    'error': f'Cannot cancel within {Config.CANCELLATION_WINDOW_HOURS} hours of appointment'
                }, 400
            
            appointment.status = 'cancelled'
            appointment.cancellation_reason = reason
            
            db.session.commit()
            
            # Send cancellation notifications
            customer = User.query.get(appointment.customer_id)
            appointment_data = appointment.to_dict(include_relations=True)
            
            # Email notification
            if customer and customer.email:
                from app.utils.notifications import send_cancellation_notification
                send_cancellation_notification(customer.email, appointment_data)
            
            # SMS notification
            if customer and customer.phone:
                from app.utils.notifications import send_cancellation_sms
                send_cancellation_sms(customer.phone, appointment_data)
            
            return {
                'message': 'Appointment cancelled successfully',
                'appointment': appointment_data
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to cancel appointment: {str(e)}'}, 500
    
    @staticmethod
    def get_available_slots(service_id, date_str, provider_id=None):
        """Get available time slots for a service on a given date"""
        try:
            service = Service.query.get(service_id)
            if not service:
                return {'error': 'Service not found'}, 404
            
            target_date = datetime.fromisoformat(date_str).date()
            
            # Get business hours
            start_hour = Config.BUSINESS_HOURS_START
            end_hour = Config.BUSINESS_HOURS_END
            
            # Generate all possible slots
            slots = []
            current_time = datetime.combine(target_date, datetime.min.time()).replace(hour=start_hour)
            end_time = datetime.combine(target_date, datetime.min.time()).replace(hour=end_hour)
            
            while current_time < end_time:
                slot_end = current_time + timedelta(minutes=service.duration_minutes)
                
                if slot_end.hour <= end_hour:
                    # Check if slot is available
                    is_available = not AppointmentController._check_conflicts(
                        provider_id, current_time, slot_end
                    )
                    
                    slots.append({
                        'start_time': current_time.isoformat(),
                        'end_time': slot_end.isoformat(),
                        'available': is_available
                    })
                
                current_time += timedelta(minutes=30)  # 30-minute intervals
            
            return {'slots': slots, 'date': date_str}, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch available slots: {str(e)}'}, 500