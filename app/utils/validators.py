import re
from datetime import datetime, time
from email_validator import validate_email as email_validate, EmailNotValidError
from config import Config


def validate_email(email):
    """Validate email format"""
    try:
        email_validate(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_time_slot(start_time, end_time):
    """Validate time slot booking"""
    
    # Check if times are datetime objects
    if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        return False, "Invalid datetime objects"
    
    # Check if start is before end
    if start_time >= end_time:
        return False, "Start time must be before end time"
    
    # Check if booking is in the past
    if start_time < datetime.utcnow():
        return False, "Cannot book appointments in the past"
    
    # Check business hours
    start_hour = start_time.hour
    end_hour = end_time.hour
    
    if start_hour < Config.BUSINESS_HOURS_START or end_hour > Config.BUSINESS_HOURS_END:
        return False, f"Appointments must be between {Config.BUSINESS_HOURS_START}:00 and {Config.BUSINESS_HOURS_END}:00"
    
    # Check if booking is on weekend (optional)
    if start_time.weekday() >= 5:  # Saturday=5, Sunday=6
        return False, "Bookings not available on weekends"
    
    return True, "Time slot is valid"

def validate_phone(phone):
    """Validate phone number format"""
    # Basic validation - adjust regex based on your region
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

def validate_vehicle_year(year):
    """Validate vehicle year"""
    current_year = datetime.now().year
    if year < 1900 or year > current_year + 1:
        return False, f"Year must be between 1900 and {current_year + 1}"
    return True, "Year is valid"