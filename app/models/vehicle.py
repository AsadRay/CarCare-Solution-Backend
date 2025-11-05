from app import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    make = db.Column(db.String(50), nullable=False)  # e.g., Toyota, Honda
    model = db.Column(db.String(50), nullable=False)  # e.g., Camry, Civic
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), nullable=True)
    color = db.Column(db.String(30), nullable=True)
    vin = db.Column(db.String(17), nullable=True, unique=True)  # Vehicle Identification Number
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='vehicles')
    appointments = db.relationship('Appointment', back_populates='vehicle')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'license_plate': self.license_plate,
            'color': self.color,
            'vin': self.vin,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model}>'