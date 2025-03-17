'use client'

import { useEffect, useState, useRef } from 'react';

export default function Checkout() {
  // Simplified state
  const [orderDetails] = useState({
    orderId: 'ORD' + Date.now(),
    amount: 200000, // $2,000.00 in cents
    items: [
      { name: 'AMD Ryzen CPU', price: 29900 },
      { name: 'NVIDIA RTX GPU', price: 79900 },
      { name: 'Gaming Motherboard', price: 24900 },
      { name: 'RAM 32GB', price: 19900 },
      { name: 'SSD 1TB', price: 14900 },
      { name: 'Power Supply 750W', price: 12900 },
      { name: 'PC Case', price: 9900 },
      { name: 'CPU Cooler', price: 7900 }
    ]
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [checkoutUrl, setCheckoutUrl] = useState('');
  const hasCreatedSession = useRef(false);
  
  // Format amount for display
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-SG', {
      style: 'currency',
      currency: 'SGD'
    }).format(amount / 100);
  };

  // Load Stripe checkout session
  useEffect(() => {
    // Skip if we already created a session in this component lifecycle
    if (hasCreatedSession.current) return;
    
    console.log("Creating checkout session...");
    hasCreatedSession.current = true;
    
    // Format line items properly for Stripe
    const line_items = [{
      price_data: {
        currency: 'sgd',
        product_data: {
          name: 'Custom PC Build',
          // Removed empty description to avoid Stripe error
        },
        unit_amount: orderDetails.amount,
      },
      quantity: 1,
    }];
    
    // Create a checkout session
    fetch('http://127.0.0.1:5000/create-checkout-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        line_items: line_items,
        currency: 'sgd',
        metadata: {
          order_id: orderDetails.orderId
        },
        customer_email: 'john@example.com',
        success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/checkout?canceled=true`
      })
    })
    .then(res => {
      console.log("Server response status:", res.status);
      return res.json();
    })
    .then(data => {
      console.log("Server response data:", data);
      
      if (data.error) {
        console.error("Error from server:", data.error);
        setError(data.error);
        setLoading(false);
        return;
      }

      if (!data.url) {
        console.error("No checkout URL received from the server");
        setError('No checkout URL received from the server');
        setLoading(false);
        return;
      }
      
      console.log("Checkout session created, URL:", data.url);
      setCheckoutUrl(data.url);
      setLoading(false);
    })
    .catch(error => {
      console.error('Error during session creation:', error);
      setError('Checkout initialization failed: ' + error.message);
      setLoading(false);
    });
  }, [orderDetails.amount, orderDetails.orderId]);

  const redirectToCheckout = () => {
    if (checkoutUrl) {
      window.location.href = checkoutUrl;
    }
  };

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 bg-gray-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-2xl font-bold tracking-tight text-white">
          Complete Your Purchase
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-gray-800 px-6 py-6 shadow rounded-lg sm:px-8">
          {loading ? (
            <div className="text-center">
              <p className="text-white mb-4">Loading checkout...</p>
              <p className="text-xs text-gray-400">If loading takes too long, check console for errors</p>
            </div>
          ) : error ? (
            <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-500"
              >
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="mb-6">
                <h3 className="text-lg font-medium text-white mb-2">Order Summary</h3>
                <div className="space-y-2">
                  {orderDetails.items.map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-gray-300">{item.name}</span>
                      <span className="text-white">{formatAmount(item.price)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between pt-2 border-t border-gray-700">
                    <span className="font-bold text-white">Total</span>
                    <span className="font-bold text-white">{formatAmount(orderDetails.amount)}</span>
                  </div>
                </div>
              </div>

              {checkoutUrl ? (
                <div className="space-y-6">
                  <div className="bg-white rounded-md p-4 text-center">
                    <p className="text-gray-800 mb-4">Your order is ready for payment</p>
                    <p className="text-sm text-gray-500">Click the button below to proceed to our secure checkout</p>
                  </div>
                  
                  <button
                    onClick={redirectToCheckout}
                    className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                  >
                    Proceed to Secure Checkout
                  </button>
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-white mb-4">Preparing checkout...</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}