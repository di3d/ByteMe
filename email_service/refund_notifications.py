from .sendgrid_client import EmailService
from .config import EmailConfig

class RefundNotifications:
    """
    Refund notification service that handles all refund-related emails
    """
    
    @staticmethod
    def send_refund_processed(customer_email, refund_data):
        """
        Send notification that a refund has been processed
        
        Args:
            customer_email (str): Customer's email address
            refund_data (dict): Data about the refund
                - refund_id: Stripe refund ID
                - amount: Amount refunded
                - payment_id: Original payment ID
                - currency: Currency code (e.g., 'sgd')
                - status: Refund status (e.g., 'succeeded')
                
        Returns:
            dict: Response with status and message
        """
        # Check if we should use template or plain text
        if EmailConfig.TEMPLATE_REFUND_PROCESSED:
            # Use template
            template_data = {
                "refund_id": refund_data.get("refund_id"),
                "refund_amount": format_amount(refund_data.get("amount"), refund_data.get("currency", "sgd")),
                "payment_id": refund_data.get("payment_id"),
                "status": refund_data.get("status", "processed")
            }
            
            return EmailService.send_email(
                customer_email,
                "Your Refund Has Been Processed",
                template_id=EmailConfig.TEMPLATE_REFUND_PROCESSED,
                template_data=template_data
            )
        else:
            # Use plain text
            content = f"""
Dear Customer,

Good news! Your refund has been processed successfully.

Refund details:
- Refund ID: {refund_data.get("refund_id")}
- Amount: {format_amount(refund_data.get("amount"), refund_data.get("currency", "sgd"))}
- Status: {refund_data.get("status", "processed")}

The funds should appear in your account within 5-10 business days, depending on your bank's processing time.

Thank you for your patience!
ByteMe Store Team
            """
            
            return EmailService.send_email(
                customer_email,
                "Your Refund Has Been Processed",
                content=content
            )
    
    @staticmethod
    def send_refund_failed(customer_email, refund_data):
        """
        Send notification that a refund has failed
        
        Args:
            customer_email (str): Customer's email address
            refund_data (dict): Data about the refund
                - request_id: Refund request ID
                - payment_id: Original payment ID
                - error: Error message
                
        Returns:
            dict: Response with status and message
        """
        # Check if we should use template or plain text
        if EmailConfig.TEMPLATE_REFUND_FAILED:
            # Use template
            template_data = {
                "refund_request_id": refund_data.get("request_id"),
                "payment_id": refund_data.get("payment_id"),
                "error_message": refund_data.get("error", "Unknown error")
            }
            
            return EmailService.send_email(
                customer_email,
                "Issue with Your Refund Request",
                template_id=EmailConfig.TEMPLATE_REFUND_FAILED,
                template_data=template_data
            )
        else:
            # Use plain text
            content = f"""
Dear Customer,

We encountered an issue processing your refund request.

Refund request details:
- Request ID: {refund_data.get("request_id")}
- Payment ID: {refund_data.get("payment_id")}
- Error: {refund_data.get("error", "Unknown error")}

Our team has been notified and will review this issue. We will contact you shortly to resolve this matter.

If you have any questions, please contact our support team.

Thank you for your understanding,
ByteMe Store Team
            """
            
            return EmailService.send_email(
                customer_email,
                "Issue with Your Refund Request",
                content=content
            )

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