from app import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.String(20), nullable=False, default='pending')
    # Status options: pending, confirmed, in_progress, completed, cancelled
    
    notes = db.Column(db.Text, nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], back_populates='appointments')
    provider = db.relationship('User', foreign_keys=[provider_id], back_populates='provider_appointments')
    service = db.relationship('Service', back_populates='appointments')
    vehicle = db.relationship('Vehicle', back_populates='appointments')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'provider_id': self.provider_id,
            'service_id': self.service_id,
            'vehicle_id': self.vehicle_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'cancellation_reason': self.cancellation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_relations:
            data['customer'] = self.customer.to_dict() if self.customer else None
            data['provider'] = self.provider.to_dict() if self.provider else None
            data['service'] = self.service.to_dict() if self.service else None
            data['vehicle'] = self.vehicle.to_dict() if self.vehicle else None
        
        return data
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'