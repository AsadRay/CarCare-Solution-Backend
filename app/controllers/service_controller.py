from app import db
from app.models.service import Service

class ServiceController:
    
    @staticmethod
    def get_all_services(active_only=True):
        try:
            query = Service.query
            
            if active_only:
                query = query.filter_by(is_active=True)
            
            services = query.order_by(Service.category, Service.name).all()
            
            return {
                'services': [service.to_dict() for service in services]
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch services: {str(e)}'}, 500
    
    @staticmethod
    def get_service_by_id(service_id):
        """Get service by ID"""
        try:
            service = Service.query.get(service_id)
            
            if not service:
                return {'error': 'Service not found'}, 404
            
            return {'service': service.to_dict()}, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch service: {str(e)}'}, 500
    
    @staticmethod
    def get_services_by_category(category):
        """Get services by category"""
        try:
            services = Service.query.filter_by(
                category=category,
                is_active=True
            ).all()
            
            return {
                'services': [service.to_dict() for service in services],
                'category': category
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to fetch services: {str(e)}'}, 500
    
    @staticmethod
    def create_service(data):
        """Create a new service (admin only)"""
        try:
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            duration_minutes = data.get('duration_minutes')
            price = data.get('price')
            category = data.get('category', '').strip()
            
            # Validation
            if not all([name, duration_minutes, price]):
                return {'error': 'Missing required fields'}, 400
            
            if duration_minutes <= 0:
                return {'error': 'Duration must be positive'}, 400
            
            if price <= 0:
                return {'error': 'Price must be positive'}, 400
            
            # Create service
            service = Service(
                name=name,
                description=description,
                duration_minutes=duration_minutes,
                price=price,
                category=category
            )
            
            db.session.add(service)
            db.session.commit()
            
            return {
                'message': 'Service created successfully',
                'service': service.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to create service: {str(e)}'}, 500
    
    @staticmethod
    def update_service(service_id, data):
        """Update a service (admin only)"""
        try:
            service = Service.query.get(service_id)
            
            if not service:
                return {'error': 'Service not found'}, 404
            
            # Update fields
            if 'name' in data:
                service.name = data['name'].strip()
            if 'description' in data:
                service.description = data['description'].strip()
            if 'duration_minutes' in data:
                if data['duration_minutes'] <= 0:
                    return {'error': 'Duration must be positive'}, 400
                service.duration_minutes = data['duration_minutes']
            if 'price' in data:
                if data['price'] <= 0:
                    return {'error': 'Price must be positive'}, 400
                service.price = data['price']
            if 'category' in data:
                service.category = data['category'].strip()
            if 'is_active' in data:
                service.is_active = data['is_active']
            
            db.session.commit()
            
            return {
                'message': 'Service updated successfully',
                'service': service.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to update service: {str(e)}'}, 500
    
    @staticmethod
    def delete_service(service_id):
        """Delete a service (admin only)"""
        try:
            service = Service.query.get(service_id)
            
            if not service:
                return {'error': 'Service not found'}, 404
            
            # Soft delete by deactivating
            service.is_active = False
            db.session.commit()
            
            return {'message': 'Service deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to delete service: {str(e)}'}, 500