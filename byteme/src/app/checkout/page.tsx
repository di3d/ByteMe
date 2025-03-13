'use client'

import { useEffect, useState } from 'react';

export default function Checkout() {
  const [clientSecret, setClientSecret] = useState('');
  const [orderDetails, setOrderDetails] = useState({
    orderId: '',
    amount: 0,
    items: []
  });
  const [loading, setLoading] = useState(true);

  // Format amount for display
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-SG', {
      style: 'currency',
      currency: 'SGD'
    }).format(amount / 100);
  };

  useEffect(() => {
    // In a real app, you might get the order ID from URL params or context
    const orderId = 'ORD' + Date.now();
    
    // Example order - in your real app, fetch this from your PC Builder service
    const mockOrderDetails = {
      orderId: orderId,
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
    };
    
    setOrderDetails(mockOrderDetails);

    // Create PaymentIntent on the server
    fetch('http://127.0.0.1:5000/create-payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: mockOrderDetails.amount,
        currency: 'sgd',
        order_id: orderId
      })
    })
    .then(res => res.json())
    .then(data => {
      setClientSecret(data.clientSecret);
      setLoading(false);
    })
    .catch(error => {
      console.error('Error:', error);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    // Load Stripe.js after component mounts
    if (clientSecret) {
      const loadStripe = async () => {
        const stripe = await import('@stripe/stripe-js').then(module => module.loadStripe);
        const stripeInstance = await stripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);
        
        if (stripeInstance) {
          const elements = stripeInstance.elements({ clientSecret });
          const paymentElement = elements.create('payment');
          paymentElement.mount('#payment-element');
          
          // Set up the form
          const form = document.getElementById('payment-form');
          const submitButton = document.getElementById('submit');
          const messageElement = document.getElementById('payment-message');
          
          if (form && submitButton && messageElement) {
            form.addEventListener('submit', async (event) => {
              event.preventDefault();
              
              if (submitButton instanceof HTMLButtonElement) {
                submitButton.disabled = true;
              }
              
              const { error } = await stripeInstance.confirmPayment({
                elements,
                confirmParams: {
                  return_url: `${window.location.origin}/success`,
                }
              });
              
              if (error) {
                messageElement.textContent = error.message;
                if (submitButton instanceof HTMLButtonElement) {
                  submitButton.disabled = false;
                }
              }
            });
          }
        }
      };
      
      loadStripe();
    }
  }, [clientSecret]);

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
            <p className="text-center text-white">Loading checkout...</p>
          ) : (
            <>
              <div className="mb-6">
                <h3 className="text-lg font-medium text-white mb-2">Order Summary</h3>
                <div className="space-y-2">
                  {orderDetails.items.map((item: any, index: number) => (
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

              <form id="payment-form" className="space-y-6">
                <div id="payment-element" className="bg-white rounded-md p-4"></div>
                <button
                  id="submit"
                  type="submit"
                  className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Pay now
                </button>
                <div id="payment-message" className="text-sm text-red-500 text-center"></div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}