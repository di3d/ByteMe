'use client'

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function RefundPage() {
  const searchParams = useSearchParams();
  const [paymentIntentId, setPaymentIntentId] = useState('');
  const [orderId, setOrderId] = useState('');
  const [amount, setAmount] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ success?: boolean; message?: string } | null>(null);

  useEffect(() => {
    // Pre-fill payment_intent from URL if available
    const payment_intent = searchParams.get('payment_intent');
    if (payment_intent) {
      setPaymentIntentId(payment_intent);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!paymentIntentId.trim().startsWith('pi_')) {
      setResult({
        success: false,
        message: 'Invalid Payment Intent ID format. Must start with "pi_"'
      });
      return;
    }

    setSubmitting(true);
    
    try {
      const response = await fetch('http://127.0.0.1:5000/refund', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_intent_id: paymentIntentId,
          order_id: orderId || undefined,
          amount: amount ? parseInt(amount) * 100 : undefined, // Convert to cents
        }),
      });

      const data = await response.json();
      
      setResult({
        success: response.ok,
        message: data.message || (response.ok ? 'Refund processed successfully!' : 'Refund failed. Please try again.')
      });
    } catch (error) {
      setResult({
        success: false,
        message: 'Error processing refund. Please try again later.'
      });
      console.error('Refund error:', error);
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
                  min="0"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="block w-full rounded-md px-3 py-2 text-black"
                  placeholder="Leave blank for full refund"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Leave blank for full refund
                </p>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={submitting}
                className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
              >
                {submitting ? 'Processing...' : 'Process Refund'}
              </button>
            </div>
          </form>

          {result && (
            <div className={`mt-6 p-3 rounded-md ${result.success ? 'bg-green-800' : 'bg-red-800'}`}>
              <p className="text-white">{result.message}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}