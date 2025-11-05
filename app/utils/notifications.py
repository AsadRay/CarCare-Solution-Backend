import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from config import Config

def send_email(to_email, subject, html_content):
    """Send email using SendGrid"""
    try:
        if not Config.SENDGRID_API_KEY:
            print("SendGrid API key not configured")
            return False
        
        message = Mail(
            from_email=Config.SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        
        return response.status_code == 202
        
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def send_sms(to_phone, message):
    """Send SMS using Twilio"""
    try:
        if not all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN]):
            print("Twilio credentials not configured")
            return False
        
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=Config.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        
        return message.sid is not None
        
    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        return False

def send_appointment_confirmation(email, appointment_data):
    """Send appointment confirmation email"""
    subject = "Appointment Confirmation - AutoBook"
    
    service = appointment_data.get('service', {})
    vehicle = appointment_data.get('vehicle', {})
    start_time = appointment_data.get('start_time', '')
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Appointment Confirmed!</h2>
                <p>Your appointment has been successfully booked.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Appointment Details:</h3>
                    <p><strong>Service:</strong> {service.get('name', 'N/A')}</p>
                    <p><strong>Date & Time:</strong> {start_time}</p>
                    <p><strong>Duration:</strong> {service.get('duration_minutes', 0)} minutes</p>
                    <p><strong>Price:</strong> ${service.get('price', 0)}</p>
                    <p><strong>Vehicle:</strong> {vehicle.get('year', '')} {vehicle.get('make', '')} {vehicle.get('model', '')}</p>
                </div>
                
                <p><strong>Important:</strong> Please arrive 10 minutes before your appointment time.</p>
                
                <p>If you need to cancel or reschedule, please contact us at least 24 hours in advance.</p>
                
                <p>Thank you for choosing AutoBook!</p>
            </div>
        </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_appointment_reminder(email, appointment_data):
    """Send appointment reminder email"""
    subject = "Appointment Reminder - AutoBook"
    
    service = appointment_data.get('service', {})
    start_time = appointment_data.get('start_time', '')
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #FF9800;">Appointment Reminder</h2>
                <p>This is a reminder about your upcoming appointment.</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Service:</strong> {service.get('name', 'N/A')}</p>
                    <p><strong>Date & Time:</strong> {start_time}</p>
                </div>
                
                <p>We look forward to seeing you!</p>
            </div>
        </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_cancellation_notification(email, appointment_data):
    """Send appointment cancellation email"""
    subject = "Appointment Cancelled - AutoBook"
    
    start_time = appointment_data.get('start_time', '')
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #f44336;">Appointment Cancelled</h2>
                <p>Your appointment scheduled for <strong>{start_time}</strong> has been cancelled.</p>
                
                <p>If you'd like to reschedule, please visit our website or contact us.</p>
                
                <p>Thank you for your understanding.</p>
            </div>
        </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_appointment_sms(phone, appointment_data):
    """Send appointment confirmation SMS"""
    try:
        service = appointment_data.get('service', {})
        start_time = appointment_data.get('start_time', '')
        
        # Format message (SMS should be short)
        message = f"AutoBook: Appointment confirmed! {service.get('name', 'Service')} on {start_time[:10]} at {start_time[11:16]}. Reply CANCEL to cancel."
        
        return send_sms(phone, message)
    except Exception as e:
        print(f"SMS notification failed: {str(e)}")
        return False

def send_reminder_sms(phone, appointment_data):
    """Send appointment reminder SMS"""
    try:
        service = appointment_data.get('service', {})
        start_time = appointment_data.get('start_time', '')
        
        message = f"AutoBook Reminder: Your {service.get('name', 'appointment')} is tomorrow at {start_time[11:16]}. See you then!"
        
        return send_sms(phone, message)
    except Exception as e:
        print(f"SMS reminder failed: {str(e)}")
        return False

def send_cancellation_sms(phone, appointment_data):
    """Send appointment cancellation SMS"""
    try:
        start_time = appointment_data.get('start_time', '')
        
        message = f"AutoBook: Your appointment on {start_time[:10]} has been cancelled. Visit our website to reschedule."
        
        return send_sms(phone, message)
    except Exception as e:
        print(f"SMS cancellation notification failed: {str(e)}")
        return False

def send_status_update_sms(phone, appointment_data, new_status):
    """Send appointment status update SMS"""
    try:
        status_messages = {
            'confirmed': 'Your appointment has been confirmed!',
            'in_progress': 'Your service has started. We\'ll notify you when complete.',
            'completed': 'Your service is complete! Thank you for choosing AutoBook.',
            'cancelled': 'Your appointment has been cancelled.'
        }
        
        message = f"AutoBook: {status_messages.get(new_status, 'Appointment status updated')}"
        
        return send_sms(phone, message)
    except Exception as e:
        print(f"SMS status update failed: {str(e)}")
        return False