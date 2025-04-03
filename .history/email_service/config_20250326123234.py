import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

class EmailConfig:
    """Email service configuration"""
    # SendGrid settings
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    
    # Email sender settings
    EMAIL_FROM_ADDRESS = os.getenv('SENDGRID_SENDER_EMAIL', 'noreply@byteme.store')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'ByteMe Store')
    
    # Email templates
    TEMPLATE_REFUND_INITIATED = os.getenv('TEMPLATE_REFUND_INITIATED')
    TEMPLATE_REFUND_PROCESSED = os.getenv('TEMPLATE_REFUND_PROCESSED')
    TEMPLATE_REFUND_FAILED = os.getenv('TEMPLATE_REFUND_FAILED')
    
    # Service configuration
    DEBUG_MODE = os.getenv('EMAIL_DEBUG', 'False').lower() in ('true', '1', 't')
    QUEUE_EMAIL_REQUESTS = os.getenv('QUEUE_EMAIL_REQUESTS', 'email_requests')