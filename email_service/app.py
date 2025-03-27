import os
from dotenv import load_dotenv
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sys
from datetime import datetime
import json  # Add this import

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify environment variables are loaded
logger.info("Checking SendGrid configuration...")
api_key = os.getenv('SENDGRID_API_KEY')
sender_email = os.getenv('SENDGRID_SENDER_EMAIL')

if not api_key:
    logger.error("SENDGRID_API_KEY not found in environment")
else:
    logger.info("SENDGRID_API_KEY found")
    
if not sender_email:
    logger.error("SENDGRID_SENDER_EMAIL not found in environment")
else:
    logger.info("SENDGRID_SENDER_EMAIL found")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../amqp')))
import amqp_setup

# Configure logging with format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Set PIKA logging to WARNING level only
logging.getLogger("pika").setLevel(logging.WARNING)
# Keep our app logging at DEBUG for important info
logger.setLevel(logging.DEBUG)

# Add formatter for cleaner logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
CORS(app)

# Add port configuration
PORT = 5001  # Different from Stripe's 5000

# Test route to verify service is running
@app.route('/health', methods=['GET'])
def health_check():
    """Check if service and its dependencies are healthy"""
    try:
        # Check RabbitMQ connection
        amqp_setup.check_setup()
        rabbitmq_status = "connected"
    except Exception as e:
        rabbitmq_status = f"error: {str(e)}"

    # Check SendGrid configuration
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    sendgrid_status = "configured" if sendgrid_key else "missing API key"

    return {
        "status": "healthy",
        "service": "email-notifications",
        "dependencies": {
            "rabbitmq": rabbitmq_status,
            "sendgrid": sendgrid_status
        }
    }

# Add SendGrid configuration check
def check_sendgrid_config():
    api_key = os.environ.get('SENDGRID_API_KEY')
    sender_email = os.environ.get('SENDGRID_SENDER_EMAIL')
    
    if not api_key:
        logger.error("SENDGRID_API_KEY not set in environment")
        return False
    if not sender_email:
        logger.error("SENDGRID_SENDER_EMAIL not set in environment")
        return False
    return True

def verify_sendgrid():
    """Verify SendGrid configuration"""
    try:
        api_key = os.environ.get('SENDGRID_API_KEY')
        sender_email = os.environ.get('SENDGRID_SENDER_EMAIL')
        
        if not api_key:
            logger.error("❌ SENDGRID_API_KEY not set in environment")
            return False
        if not sender_email:
            logger.error("❌ SENDGRID_SENDER_EMAIL not set in environment")
            return False
            
        sg = SendGridAPIClient(api_key)
        logger.info("✅ SendGrid configuration verified")
        return True
    except Exception as e:
        logger.error(f"❌ SendGrid verification failed: {str(e)}")
        return False

# Test route to send a test email
@app.route('/test-email', methods=['GET'])
def test_email():
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        message = Mail(
            from_email=os.environ.get('SENDGRID_SENDER_EMAIL'),
            to_emails='jonongca@gmail.com',  # Your test email
            subject='ByteMe Email Service Test',
            html_content=f"""
                <h2>ByteMe Email Service Test</h2>
                <p>Good news! Your email service is working correctly.</p>
                <p><strong>Configuration Details:</strong></p>
                <ul>
                    <li>Service: Email Notifications</li>
                    <li>SendGrid: Connected</li>
                    <li>Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
                </ul>
                <p>You are ready to receive refund notifications!</p>
            """
        )
        
        response = sg.send(message)
        return jsonify({
            "success": True,
            "details": {
                "status_code": response.status_code,
                "sent_to": 'jonongca@gmail.com',
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "details": {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 500

def callback(channel, method, properties, body):
    """Process email notifications"""
    try:
        logger.info("=================== New Message Received ===================")
        logger.info(f"Received message: {body}")
        
        event = json.loads(body)  # Now this will work
        logger.info(f"Processing notification event type: {event['type']}")
        
        if event['type'] == 'notification.email.refund':
            customer_email = event['data'].get('customer_email')
            if not customer_email:
                logger.error("❌ No customer email provided")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            logger.info(f"✉️ Sending refund notification to: {customer_email}")
            logger.info(f"💰 Refund amount: ${event['data']['amount']/100:.2f}")
            
            message = Mail(
                from_email=os.environ.get('SENDGRID_SENDER_EMAIL'),
                to_emails=customer_email,
                subject='Your ByteMe Refund Has Been Approved',
                html_content=f"""
                    <h2>Your Refund Has Been Approved</h2>
                    <p>Great news! Your refund request has been approved and is being processed by your bank.</p>
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Refund Details:</strong></p>
                        <ul style="list-style: none; padding-left: 0;">
                            <li>Payment ID: {event['data']['payment_intent_id']}</li>
                            <li>Amount: ${event['data']['amount']/100:.2f}</li>
                            <li>Status: Approved</li>
                        </ul>
                    </div>
                    <p>The refund amount should appear in your account within 5-10 business days, depending on your bank's processing time.</p>
                    <p>If you have any questions about your refund, please don't hesitate to contact our support team.</p>
                    <p>Thank you for your business!</p>
                    <br>
                    <p>Best regards,</p>
                    <p>The ByteMe Team</p>
                """
            )
            
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            logger.info(f"📧 Email sent! Status code: {response.status_code}")
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
    except Exception as e:
        logger.error(f"❌ Error processing notification: {str(e)}")
        logger.error("=================== Error Details ===================")
        logger.error(f"Message body: {body}")
        logger.error(f"Exception: {str(e)}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_email_worker():
    """Start consuming email notifications"""
    try:
        # First verify SendGrid
        if not verify_sendgrid():
            logger.error("❌ Cannot start email worker - SendGrid not configured")
            return
            
        # Initialize AMQP
        amqp_setup.check_setup()
        channel = amqp_setup.channel
        
        # Declare queue (in case it doesn't exist)
        channel.queue_declare(queue='EmailNotifications', durable=True)
        
        logger.info("✅ Starting to consume email notifications...")
        channel.basic_consume(
            queue='EmailNotifications',
            on_message_callback=callback,
            auto_ack=False
        )
        
        channel.start_consuming()
        
    except Exception as e:
        logger.error(f"❌ Error starting email worker: {str(e)}")

if __name__ == '__main__':
    print("Starting Email Notification Service...")
    # Start Flask app in one thread
    import threading
    threading.Thread(target=lambda: app.run(port=PORT, debug=False)).start()
    
    # Start the email worker in main thread
    start_email_worker()
