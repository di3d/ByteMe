from email_service.sendgrid_client import EmailService
from email_service.config import EmailConfig
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# Configure logger
logger = logging.getLogger(__name__)

def format_amount(amount, currency='sgd'):
    """Format currency amount for display"""
    if not amount:
        return "0.00"

    # Convert cents to dollars
    dollars = float(amount) / 100

    # Format based on currency
    if currency.lower() == 'sgd':
        return f"SGD ${dollars:.2f}"
    else:
        return f"{currency.upper()} {dollars:.2f}"

class RefundNotifications:
    """
    Refund notification service that handles all refund-related emails
    """

    @staticmethod
    def send_refund_initiated(customer_email, refund_data):
        try:
            sg = SendGridAPIClient(EmailConfig.SENDGRID_API_KEY)
            message = Mail(
                from_email=EmailConfig.EMAIL_FROM_ADDRESS,
                to_emails=customer_email,
                subject='Your Refund Has Been Initiated',
                html_content=f"""
                    <h2>Refund Initiated</h2>
                    <p>Your refund of ${refund_data['amount']/100:.2f} has been initiated.</p>
                    <p>Payment ID: {refund_data['payment_intent_id']}</p>
                """
            )
            
            response = sg.send(message)
            logger.warning(f"SendGrid Response Code: {response.status_code}")
            if response.status_code >= 300:
                logger.error(f"SendGrid Error: {response.body}")
                raise Exception(f"SendGrid error: {response.status_code}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to send refund email: {str(e)}")
            raise