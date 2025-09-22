from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
import logging

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.client = None
        if settings.sendgrid_api_key:
            self.client = SendGridAPIClient(api_key=settings.sendgrid_api_key)
    
    async def send_subscription_acknowledgment(self, email: str, request_id: str, name: Optional[str] = None) -> bool:
        """Send acknowledgment email for subscription request"""
        if not self.client:
            logger.warning("SendGrid API key not configured, email not sent")
            return False
        
        # Create approval and rejection URLs (these would be actual URLs in production)
        approve_url = f"https://yourdomain.com/admin/approve/{request_id}"
        reject_url = f"https://yourdomain.com/admin/reject/{request_id}"
        
        subject = "Subscription Request Acknowledgment - Data Mining Wales"
        
        html_content = f"""
        <html>
        <body>
            <h2>Subscription Request Received</h2>
            <p>Dear {name or email},</p>
            
            <p>Thank you for your interest in Data Mining Wales. We have received your subscription request.</p>
            
            <p><strong>Request ID:</strong> {request_id}</p>
            
            <p>Your request is currently under review. You will receive another email once we have processed your request.</p>
            
            <p>If you have any questions, please don't hesitate to contact us.</p>
            
            <p>Best regards,<br>
            Data Mining Wales Team</p>
            
            <hr>
            <p><small>This is an automated message. Please do not reply to this email.</small></p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=settings.from_email,
            to_emails=email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            logger.info(f"Acknowledgment email sent to {email}, status: {response.status_code}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send acknowledgment email to {email}: {str(e)}")
            return False
    
    async def send_admin_notification(self, subscription_data: dict, request_id: str) -> bool:
        """Send notification to admin about new subscription"""
        if not self.client:
            logger.warning("SendGrid API key not configured, admin notification not sent")
            return False
        
        admin_email = "admin@dataminingwales.org"  # This should be configurable
        subject = f"New Subscription Request - {request_id}"
        
        html_content = f"""
        <html>
        <body>
            <h2>New Subscription Request</h2>
            
            <p><strong>Request ID:</strong> {request_id}</p>
            <p><strong>Email:</strong> {subscription_data.get('email')}</p>
            <p><strong>Name:</strong> {subscription_data.get('name', 'Not provided')}</p>
            <p><strong>Organization:</strong> {subscription_data.get('organization', 'Not provided')}</p>
            <p><strong>Interests:</strong> {subscription_data.get('interests', 'Not provided')}</p>
            
            <p><a href="https://yourdomain.com/admin/subscriptions/">Review in Admin Panel</a></p>
            
            <p>Please review and approve/reject this subscription request.</p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=settings.from_email,
            to_emails=admin_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.client.send(message)
            logger.info(f"Admin notification sent, status: {response.status_code}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
            return False


# Global email service instance
email_service = EmailService()