from app import db
from app.models.vehicle import Vehicle
from app.utils.validators import validate_vehicle_year

class VehicleController:
    
    @staticmethod
    def create_vehicle(user_id, data):
        """Create a new vehicle for user"""
        try:
            make = data.get('make', '').strip()
            model = data.get('model', '').strip()
            year = data.get('year')
            license_plate = data.get('license_plate', '').strip()
            color = data.get('color', '').strip()
            vin = data.get('vin', '').strip()
            notes = data.get('notes', '').strip()
            
            # Validate required fields
            if not all([make, model, year]):
                return {'error': 'Make, model, and year are required'}, 400
            
            # Validate year
            year_valid, year_msg = validate_vehicle_year(year)
            if not year_valid:
                return {'error': year_msg}, 400
            
            # Check if VIN already exists (if provided)
            if vin:
                existing_vehicle = Vehicle.query.filter_by(vin=vin).first()
                if existing_vehicle:
                    return {'error': 'Vehicle with this VIN already exists'}, 409
            
            # Create vehicle
            vehicle = Vehicle(
                user_id=user_id,
                make=make,
                model=model,
                year=year,
                license_plate=license_plate,
                color=color,
                vin=vin if vin else None,
                notes=notes
            )
            
            db.session.add(vehicle)
            db.session.commit()
            
            return {
                'message': 'Vehicle added successfully',
                'vehicle': vehicle.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to create vehicle: {str(e)}'}, 500
    
    @staticmethod
    def get_user_vehicles(user_id):
        """Get all vehicles for a user"""
        try:
            vehicles = Vehicle.query.filter_by(user_id=user_id).order_by(
                Vehicle.created_at.desc()
            ).all()
            
            return {
                'vehicles': [vehicle.to_dict() for vehicle in vehicles],
                'total': len(vehicles)
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch vehicles: {str(e)}'}, 500
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id, user_id):
        """Get specific vehicle by ID"""
        try:
            vehicle = Vehicle.query.filter_by(
                id=vehicle_id,
                user_id=user_id
            ).first()
            
            if not vehicle:
                return {'error': 'Vehicle not found'}, 404
            
            return {'vehicle': vehicle.to_dict()}, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch vehicle: {str(e)}'}, 500
    
    @staticmethod
    def update_vehicle(vehicle_id, user_id, data):
        """Update vehicle information"""
        try:
            vehicle = Vehicle.query.filter_by(
                id=vehicle_id,
                user_id=user_id
            ).first()
            
            if not vehicle:
                return {'error': 'Vehicle not found'}, 404
            
            # Update allowed fields
            if 'make' in data:
                vehicle.make = data['make'].strip()
            if 'model' in data:
                vehicle.model = data['model'].strip()
            if 'year' in data:
                year_valid, year_msg = validate_vehicle_year(data['year'])
                if not year_valid:
                    return {'error': year_msg}, 400
                vehicle.year = data['year']
            if 'license_plate' in data:
                vehicle.license_plate = data['license_plate'].strip()
            if 'color' in data:
                vehicle.color = data['color'].strip()
            if 'vin' in data:
                vin = data['vin'].strip()
                # Check if VIN is being changed to existing one
                if vin and vin != vehicle.vin:
                    existing = Vehicle.query.filter_by(vin=vin).first()
                    if existing:
                        return {'error': 'Vehicle with this VIN already exists'}, 409
                vehicle.vin = vin if vin else None
            if 'notes' in data:
                vehicle.notes = data['notes'].strip()
            
            db.session.commit()
            
            return {
                'message': 'Vehicle updated successfully',
                'vehicle': vehicle.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update vehicle: {str(e)}'}, 500
    
    @staticmethod
    def delete_vehicle(vehicle_id, user_id):
        """Delete a vehicle"""
        try:
            vehicle = Vehicle.query.filter_by(
                id=vehicle_id,
                user_id=user_id
            ).first()
            
            if not vehicle:
                return {'error': 'Vehicle not found'}, 404
            
            # Check if vehicle has any appointments
            from app.models.appointment import Appointment
            has_appointments = Appointment.query.filter_by(
                vehicle_id=vehicle_id
            ).first()
            
            if has_appointments:
                return {
                    'error': 'Cannot delete vehicle with existing appointments. Cancel appointments first.'
                }, 400
            
            db.session.delete(vehicle)
            db.session.commit()
            
            return {'message': 'Vehicle deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete vehicle: {str(e)}'}, 500
    
    @staticmethod
    def get_vehicle_appointments(vehicle_id, user_id):
        """Get all appointments for a specific vehicle"""
        try:
            vehicle = Vehicle.query.filter_by(
                id=vehicle_id,
                user_id=user_id
            ).first()
            
            if not vehicle:
                return {'error': 'Vehicle not found'}, 404
            
            appointments = vehicle.appointments
            
            return {
                'vehicle': vehicle.to_dict(),
                'appointments': [apt.to_dict(include_relations=True) for apt in appointments],
                'total_appointments': len(appointments)
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch vehicle appointments: {str(e)}'}, 500