from email_service.sendgrid_client import EmailService
from email_service.config import EmailConfig

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
        """
        Send notification that a refund has been initiated

        Args:
            customer_email (str): Customer's email address
            refund_data (dict): Data about the refund
                - payment_intent_id: Payment Intent ID
                - amount: Amount being refunded
                - currency: Currency code (e.g., 'sgd')

        Returns:
            dict: Response with status and message
        """
        # Check if we should use template or plain text
        if EmailConfig.TEMPLATE_REFUND_INITIATED:
            # Use template
            template_data = {
                "payment_intent_id": refund_data.get("payment_intent_id"),
                "refund_amount": format_amount(refund_data.get("amount"), refund_data.get("currency", "sgd"))
            }

            return EmailService.send_email(
                customer_email,
                "Your Refund Has Been Initiated",
                template_id=EmailConfig.TEMPLATE_REFUND_INITIATED,
                template_data=template_data
            )
        else:
            # Use plain text
            content = f"""
Dear Customer,

We have received your refund request and it is now being processed.

Refund details:
- Payment Intent ID: {refund_data.get("payment_intent_id")}
- Amount: {format_amount(refund_data.get("amount"), refund_data.get("currency", "sgd"))}

We will notify you once the refund has been completed. Please allow 5-10 business days for the funds to appear in your account.

Thank you,
ByteMe Store Team
            """

            return EmailService.send_email(
                customer_email,
                "Your Refund Has Been Initiated",
                content=content
            )