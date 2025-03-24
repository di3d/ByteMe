'use client'

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function RefundForm() {
  const searchParams = useSearchParams();
  const [paymentIntentId, setPaymentIntentId] = useState('');
  const [amount, setAmount] = useState('');
  const [orderId, setOrderId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [checkedPaymentDetails, setCheckedPaymentDetails] = useState(false);

  // Fetch payment intent ID from URL if available
  useEffect(() => {
    const paymentIntent = searchParams.get('payment_intent');
    const sessionId = searchParams.get('session_id');
    const orderId = searchParams.get('order_id');
    
    if (orderId) {
      setOrderId(orderId);
    }
    
    if (paymentIntent) {
      // Direct payment intent ID
      setPaymentIntentId(paymentIntent);
      setCheckedPaymentDetails(true);
    } else if (sessionId && !checkedPaymentDetails) {
      // If we have a session ID, try to get the payment intent from it
      setCheckedPaymentDetails(true);
      
      fetch(`http://127.0.0.1:5000/checkout-session?session_id=${sessionId}`)
        .then(res => res.json())
        .then(data => {
          console.log("Checkout session data:", data); // For debugging
          if (data.payment_intent) {
            setPaymentIntentId(data.payment_intent);
            
            // If order ID is in the metadata, use that too
            if (data.metadata && data.metadata.order_id && !orderId) {
              setOrderId(data.metadata.order_id);
            }
          }
        })
        .catch(err => {
          console.error("Error fetching session details:", err);
        });
    }
  }, [searchParams, checkedPaymentDetails]);

  // Format currency amount for display
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-SG', {
      style: 'currency',
      currency: 'SGD'
    }).format(amount / 100);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setResult(null);

    try {
      // Validate payment intent ID format - more permissive validation
      if (!paymentIntentId || paymentIntentId.trim() === '') {
        setResult({
          success: false,
          message: "Please enter a valid payment intent ID"
        });
        setSubmitting(false);
        return;
      }
      
      // Convert amount from dollars to cents if provided
      const amountInCents = amount ? Math.round(parseFloat(amount) * 100) : undefined;
      
      // Generate a unique request ID
      const requestId = `REQ-${Date.now()}`;
      
      // Call the refund-async endpoint
      const response = await fetch('http://127.0.0.1:5000/refund-async', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          payment_intent_id: paymentIntentId,
          amount: amountInCents,
          order_id: orderId,
          request_id: requestId
        })
      });

      // Check if we got a 404, which might indicate endpoint path change
      if (response.status === 404) {
        throw new Error('Refund endpoint not found. The API path might have changed.');
      }

      const data = await response.json();
      
      if (data.success) {
        setResult({
          success: true,
          message: `Refund request submitted successfully. Reference ID: ${data.request_id}`,
          details: {
            requestId: data.request_id
          }
        });
      } else {
        setResult({
          success: false,
          message: data.error || 'Failed to submit refund request'
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : 'An unknown error occurred'
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 bg-gray-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-2xl font-bold tracking-tight text-white">
          Process Refund
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-gray-800 px-6 py-6 shadow rounded-lg sm:px-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="payment-intent-id" className="block text-sm font-medium text-white">
                Payment Intent ID
              </label>
              <div className="mt-2">
                <input
                  id="payment-intent-id"
                  name="paymentIntentId"
                  type="text"
                  required
                  value={paymentIntentId}
                  onChange={(e) => setPaymentIntentId(e.target.value)}
                  className="block w-full rounded-md px-3 py-2 text-black"
                  placeholder="pi_..."
                />
                <p className="text-xs text-gray-400 mt-1">
                  Must start with "pi_" (e.g., pi_3NcM2WGswQMg8jUK0asdf123)
                </p>
              </div>
            </div>

            <div>
              <label htmlFor="order-id" className="block text-sm font-medium text-white">
                Order ID
              </label>
              <div className="mt-2">
                <input
                  id="order-id"
                  name="orderId"
                  type="text"
                  value={orderId}
                  onChange={(e) => setOrderId(e.target.value)}
                  className="block w-full rounded-md px-3 py-2 text-black"
                  placeholder="Order ID (optional)"
                />
              </div>
            </div>

            <div>
              <label htmlFor="amount" className="block text-sm font-medium text-white">
                Amount to Refund (SGD)
              </label>
              <div className="mt-2">
                <input
                  id="amount"
                  name="amount"
                  type="number"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="block w-full rounded-md px-3 py-2 text-black"
                  placeholder="Leave blank for full refund"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Leave blank to refund the full amount
                </p>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting || !paymentIntentId || paymentIntentId.trim() === ''}
              className="flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600 disabled:opacity-50"
            >
              {submitting ? 'Processing...' : 'Process Refund'}
            </button>
          </form>

          {result && (
            <div className={`mt-4 p-3 rounded-md ${result.success ? 'bg-green-800' : 'bg-red-800'}`}>
              <p className="text-white text-sm">{result.message}</p>
              {result.success && (
                <div className="mt-2 text-xs text-white">
                  <p>Your refund request has been submitted for processing.</p>
                  <p className="mt-1">You will receive an email notification when the refund is complete.</p>
                </div>
              )}
            </div>
          )}

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400">
              This is an asynchronous request. The refund will be processed in the background.
              For future status updates, please check your email or order history.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}