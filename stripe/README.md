# Stripe Payment Microservice

A comprehensive wrapper service for Stripe payment processing that provides simple APIs for payments, checkouts, and asynchronous refunds using RabbitMQ.

## Features

- **Checkout Sessions**: Easy creation of Stripe-hosted checkout pages
- **Direct Payment Intents**: For custom payment UIs
- **Refund Processing**: Both synchronous and asynchronous options
- **Webhook Handling**: Process Stripe events securely
- **Asynchronous Architecture**: Background processing via RabbitMQ queues
- **RESTful APIs**: Simple HTTP endpoints for all payment operations

## Architecture

![Architecture Overview](https://i.imgur.com/8ZYs4Dw.png)

This service uses a layered architecture:

1. **Endpoints Layer**: RESTful APIs for client applications
2. **Process Layer**: Background workers for asynchronous operations
3. **Utils Layer**: Shared utilities for RabbitMQ and other functions
4. **Configuration**: Centralized settings management

## Prerequisites

- Python 3.8+
- RabbitMQ server
- Stripe account with API keys

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with your configuration:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   
   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASSWORD=guest
   ```

## Running the Service

Start the service with:

```
python app.py
```

This will:
- Initialize the RabbitMQ queues
- Start the background refund processing worker
- Start the Flask API server on port 5000

## API Endpoints

### Checkout

#### `POST /create-checkout-session`

Create a Stripe checkout session for a one-time payment.

**Request Body:**
```json
{
  "line_items": [
    {
      "price_data": {
        "currency": "sgd",
        "product_data": {
          "name": "Product Name"
        },
        "unit_amount": 10000
      },
      "quantity": 1
    }
  ],
  "success_url": "http://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "http://yourdomain.com/cancel"
}
```

**Response:**
```json
{
  "url": "https://checkout.stripe.com/..."
}
```

#### `GET /checkout-session?session_id=cs_test_...`

Retrieve details about a checkout session.

**Response:**
```json
{
  "payment_intent": "pi_...",
  "amount_total": 10000,
  "currency": "sgd",
  "customer_email": "customer@example.com",
  "payment_status": "paid",
  "metadata": {}
}
```

### Payment Intents

#### `POST /payment-intent`

Create a payment intent for custom payment flows.

**Request Body:**
```json
{
  "amount": 10000,
  "currency": "sgd"
}
```

**Response:**
```json
{
  "success": true,
  "clientSecret": "pi_..._secret_...",
  "paymentIntentId": "pi_..."
}
```

#### `GET /payment-intent/{payment_intent_id}`

Get details about a payment intent.

**Response:**
```json
{
  "id": "pi_...",
  "amount": 10000,
  "currency": "sgd",
  "status": "succeeded",
  "metadata": {}
}
```

### Refunds

#### `POST /refund`

Process a refund synchronously.

**Request Body:**
```json
{
  "payment_intent_id": "pi_...",
  "amount": 5000,
  "reason": "requested_by_customer"
}
```

**Response:**
```json
{
  "success": true,
  "refund": {
    "id": "re_...",
    "amount": 5000,
    "status": "succeeded"
  }
}
```

#### `POST /refund-async`

Queue a refund to be processed asynchronously.

**Request Body:**
```json
{
  "payment_intent_id": "pi_...",
  "amount": 5000,
  "request_id": "unique-id-123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Refund request queued successfully",
  "request_id": "unique-id-123"
}
```

#### `GET /refund-status/{request_id}?payment_intent_id=pi_...`

Check the status of an asynchronous refund.

**Response:**
```json
{
  "success": true,
  "refund_id": "re_...",
  "status": "succeeded",
  "amount": 5000,
  "request_id": "unique-id-123"
}
```

### Webhooks

#### `POST /webhook`

Handle Stripe webhook events.

**Headers:**
- `Stripe-Signature`: Webhook signature from Stripe

**Response:**
```json
{
  "success": true
}
```

## Asynchronous Refund Processing

This service implements a fire-and-forget pattern for refund processing using RabbitMQ:

1. Client makes a request to `/refund-async`
2. Request is queued in `stripe_refund_requests` queue
3. Background worker processes the refund
4. Result is published to `stripe_refund_responses` queue
5. Client can check status via `/refund-status/{request_id}`

This approach provides several benefits:
- Improved user experience (no waiting for processing)
- Better system resilience (refunds continue even if client disconnects)
- Scalable processing (multiple workers can process refunds)

### Real-world Considerations

In production environments:
- Add a persistent database to store refund requests and statuses
- Implement retry logic for failed refunds
- Add monitoring and alerting for the message queue
- Consider using webhooks from Stripe to update refund statuses

## Integration Example

### Frontend (React/Next.js)

```jsx
// Initiate checkout
const createCheckout = async () => {
  const response = await fetch('http://your-api/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      line_items: [{
        price_data: {
          currency: 'sgd',
          product_data: { name: 'Product' },
          unit_amount: 10000,
        },
        quantity: 1,
      }],
      success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${window.location.origin}/cancel`,
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
    })
  });
  
  return await response.json();
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