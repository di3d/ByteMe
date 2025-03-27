from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, TemplateId, DynamicTemplateData
from .config import EmailConfig

class EmailService:
    """SendGrid email service implementation"""
    
    @staticmethod
    def send_email(to_email, subject, content=None, template_id=None, template_data=None):
        """
        Send an email using SendGrid
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject line
            content (str, optional): Plain text content if not using template
            template_id (str, optional): SendGrid template ID
            template_data (dict, optional): Data for template variables
            
        Returns:
            dict: Response with status and message
        """
        try:
            # Validate API key
            if not EmailConfig.SENDGRID_API_KEY:
                return {
                    "success": False,
                    "message": "SendGrid API key not configured"
                }
            
            # Configure from address
            from_email = Email(
                email=EmailConfig.EMAIL_FROM_ADDRESS,
                name=EmailConfig.EMAIL_FROM_NAME
            )
            
            # Configure to address
            recipient = To(to_email)
            
            # Initialize email
            if content:
                # Create with plain text content
                plain_content = Content("text/plain", content)
                mail = Mail(from_email, recipient, subject, plain_content)
            else:
                # Create empty mail to use with template
                mail = Mail(from_email, recipient, subject)
            
            # Add template if provided
            if template_id:
                mail.template_id = TemplateId(template_id)
                
                if template_data:
                    mail.dynamic_template_data = DynamicTemplateData(template_data)
            
            # Send via SendGrid
            sg = SendGridAPIClient(EmailConfig.SENDGRID_API_KEY)
            response = sg.send(mail)
            
            # Process response
            if response.status_code >= 200 and response.status_code < 300:
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "status_code": response.status_code
                }
            else:
                print(f"Error sending email: HTTP Error {response.status_code}: {response.body.decode('utf-8') if response.body else 'No body'}")
                return {
                    "success": False,
                    "message": f"Failed to send email: HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "response_body": response.body.decode('utf-8') if response.body else "No response body"
                }
                    
        except Exception as e:
            # Log the error (replace with proper logging)
            print(f"Error sending email: {str(e)}")
            
            return {
                "success": False,
                "message": f"Error sending email: {str(e)}"
            }