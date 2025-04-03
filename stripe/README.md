# Stripe Payment Microservice

A comprehensive wrapper service for Stripe payment processing that provides simple REST APIs for payments, checkouts, and asynchronous refunds using RabbitMQ.

## Quick Start

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in a `.env` file:
   ```env
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...

   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASSWORD=guest
   ```
4. Start the service:
   ```bash
   python app.py
   ```

## Features

- **Checkout Sessions**: Create Stripe-hosted checkout pages.
- **Asynchronous Refunds**: Queue refunds for background processing.
- **RESTful APIs**: Simple HTTP endpoints for all payment operations.

## Payment Flow

### Step-by-Step Explanation

1. **Create Checkout Session**:
   - **Endpoint**: `POST /create-checkout-session`
   - **Description**: Creates a Stripe checkout session for a one-time payment.
   - **Flow**:
     - The frontend sends a request to this endpoint with the product details (e.g., price, quantity).
     - The backend uses the Stripe API to create a checkout session.
     - The session URL is returned to the frontend, which redirects the customer to Stripe's hosted checkout page.

   **Request Body**:
   ```json
   {
     "amount": 10000,
     "customer_email": "user@example.com",
     "currency": "sgd",
     "product_name": "Custom PC Build",
     "metadata": {
       "build_name": "Custom PC Build"
     },
     "success_url": "http://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
     "cancel_url": "http://yourdomain.com/checkout?canceled=true"
   }
   ```

   **Response**:
   ```json
   {
     "url": "https://checkout.stripe.com/..."
   }
   ```

2. **Retrieve Checkout Session**:
   - **Endpoint**: `GET /checkout-session?session_id=cs_test_...`
   - **Description**: Retrieves details about a checkout session.
   - **Flow**:
     - After a successful payment, the frontend retrieves the session details to display a confirmation page.
     - The backend uses the Stripe API to fetch the session details.

   **Response**:
   ```json
   {
     "payment_intent": "pi_...",
     "amount_total": 10000,
     "currency": "sgd",
     "customer_email": "user@example.com",
     "payment_status": "paid",
     "metadata": {}
   }
   ```

## Refund Flow

### Step-by-Step Explanation

1. **Initiate Refund (Asynchronous)**:
   - **Endpoint**: `POST /refund-async`
   - **Description**: Processes a refund request and returns a success response.
   - **Flow**:
     - The frontend or composite service sends a refund request to this endpoint with the payment intent ID and refund amount.
     - The backend verifies the payment intent and processes the refund using the Stripe API.

   **Request Body**:
   ```json
   {
     "payment_intent_id": "pi_...",
     "amount": 5000
   }
   ```

   **Response**:
   ```json
   {
     "success": true,
     "message": "Refund request processed successfully",
     "payment_intent": "pi_...",
     "amount": 5000
   }
   ```

2. **Check Refund Status**:
   - **Endpoint**: `GET /refund-status/{request_id}?payment_intent_id=pi_...`
   - **Description**: Checks the status of a refund.
   - **Flow**:
     - The frontend or composite service periodically checks the refund status using this endpoint.
     - The backend queries the Stripe API or a database (if implemented) to retrieve the refund status.

   **Response**:
   ```json
   {
     "success": true,
     "refund_id": "re_...",
     "status": "succeeded",
     "amount": 5000,
     "request_id": "unique-id-123"
   }
   ```

## Asynchronous Refund Processing

This service implements a simple refund processing flow:

1. Client makes an HTTP request to `/refund-async`.
2. The Stripe microservice verifies the payment intent and processes the refund using the Stripe API.
3. A success response is returned to the client (e.g., the composite service in Scenario 3).
4. The composite service can use this response to notify the user or perform additional actions.

### Real-world Considerations

In production environments:
- Add a persistent database to store refund requests and statuses.
- Implement retry logic for failed refunds.
- Add monitoring and alerting for refund processing.

## Integration Example

### Frontend (React/Next.js)

```jsx
// Initiate checkout
const createCheckout = async () => {
  const response = await fetch('http://your-api/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      amount: 10000,
      customer_email: "user@example.com",
      currency: 'sgd',
      product_name: "Custom PC Build",
      metadata: {
        build_name: "Custom PC Build"
      },
      success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${window.location.origin}/checkout?canceled=true`,
    })
  });
  
  const { url } = await response.json();
  window.location.href = url;
};

// Process refund
const processRefund = async (paymentIntentId) => {
  const response = await fetch('http://your-api/refund-async', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      payment_intent_id: paymentIntentId,
      amount: 5000
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Refund processed successfully:', data);
  } else {
    console.error('Refund failed:', data.error);
  }
};
```

## Customization

### Adding New Payment Methods

To add support for additional payment methods:

1. Update the appropriate endpoint in the `/endpoints` directory
2. Add any new configurations needed in `config.py`
3. Test with Stripe's test mode before using in production

### Enhanced Error Handling

For production environments, consider enhancing the error handling:

```python
try:
    # Process payment/refund
except stripe.error.CardError as e:
    # Handle card errors specifically
    return jsonify({"error": "Card declined", "details": str(e)}), 400
except stripe.error.StripeError as e:
    # Handle other Stripe errors
    return jsonify({"error": "Payment processing error", "details": str(e)}), 500
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {str(e)}")
    return jsonify({"error": "Server error"}), 500
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.