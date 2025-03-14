'use client'

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function Success() {
  const searchParams = useSearchParams();
  const [paymentId, setPaymentId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    // Get the session_id or payment_intent from URL using searchParams
    const session_id = searchParams.get('session_id');
    const payment_intent = searchParams.get('payment_intent');
    
    // If we have a session ID, we need to fetch the payment details
    if (session_id) {
      // In a production app, you would have an endpoint to retrieve session details
      fetch(`http://127.0.0.1:5000/checkout-session?session_id=${session_id}`)
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            setError(data.error);
          } else if (data.payment_intent) {
            setPaymentId(data.payment_intent);
          }
          setLoading(false);
        })
        .catch(err => {
          setError("Failed to fetch payment details. " + err.message);
          setLoading(false);
        });
    } 
    // If we have a payment intent directly, use that
    else if (payment_intent) {
      setPaymentId(payment_intent);
      setLoading(false);
    } 
    // No payment information
    else {
      setLoading(false);
    }
  }, [searchParams]);

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 bg-gray-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="text-green-500 text-5xl mb-4">✓</div>
        <h2 className="text-center text-2xl font-bold tracking-tight text-white">
          Payment Successful!
        </h2>
        <p className="mt-2 text-gray-300">
          Thank you for your purchase. Your PC order has been confirmed.
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-md">
        {loading ? (
          <div className="bg-gray-800 px-6 py-6 shadow rounded-lg sm:px-8 text-center">
            <p className="text-white">Loading payment details...</p>
          </div>
        ) : error ? (
          <div className="bg-gray-800 px-6 py-6 shadow rounded-lg sm:px-8 text-center">
            <p className="text-red-500">{error}</p>
            <p className="text-gray-300 mt-4">
              Your payment was successful, but we couldn't load all the details.
            </p>
          </div>
        ) : (
          <div className="bg-gray-800 px-6 py-6 shadow rounded-lg sm:px-8">
            <h3 className="text-lg font-medium text-white mb-4">Payment Information</h3>
            <div className="space-y-3">
              {paymentId ? (
                <div className="flex flex-col">
                  <p className="text-gray-300 mb-1">
                    <strong className="text-white">Payment ID:</strong>
                  </p>
                  <div className="flex items-center">
                    <code className="bg-gray-700 px-2 py-1 rounded text-yellow-300 text-sm break-all">
                      {paymentId}
                    </code>
                    <button 
                      onClick={() => {
                        navigator.clipboard.writeText(paymentId);
                        alert('Payment ID copied to clipboard!');
                      }}
                      className="ml-2 text-sm bg-gray-700 hover:bg-gray-600 text-white px-2 py-1 rounded"
                    >
                      Copy
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-gray-300">
                  No payment ID available.
                </p>
              )}
              <p className="text-gray-300 mt-4">
                We'll start building your custom PC right away and notify you when it ships.
              </p>
            </div>
          </div>
        )}
        
        <div className="mt-6 flex justify-center space-x-4">
          <Link 
            href="/" 
            className="inline-flex justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            Return to Home
          </Link>
          
          {paymentId && (
            <Link 
              href={`/refund?payment_intent=${paymentId}`} 
              className="inline-flex justify-center rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500"
            >
              Request Refund
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}