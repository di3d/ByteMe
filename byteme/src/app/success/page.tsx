'use client'

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation'; // Change this import
import Link from 'next/link';

export default function Success() {
  const searchParams = useSearchParams(); // Use this instead of router
  const [paymentId, setPaymentId] = useState('');
  const [orderId, setOrderId] = useState('');
  
  useEffect(() => {
    // Get the payment_intent from URL using searchParams
    const payment_intent = searchParams.get('payment_intent');
    
    if (payment_intent) {
      setPaymentId(payment_intent);
      // In a real app, you would fetch the order details from your backend
      setOrderId('Order-' + Date.now());
    }
  }, [searchParams]);

  // Rest of your component remains the same
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
        <div className="bg-gray-800 px-6 py-6 shadow rounded-lg sm:px-8">
          <h3 className="text-lg font-medium text-white mb-4">Order Information</h3>
          <div className="space-y-3">
            <p className="text-gray-300">
              <strong className="text-white">Order ID:</strong> {orderId}
            </p>
            <p className="text-gray-300">
              <strong className="text-white">Payment ID:</strong> {paymentId}
            </p>
            <p className="text-gray-300 mt-4">
              We'll start building your custom PC right away and notify you when it ships.
            </p>
          </div>
        </div>
        
        <div className="mt-6 text-center">
          <Link href="/" className="inline-flex justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
            Return to Home
          </Link>
        </div>
      </div>
    </div>
  );
}