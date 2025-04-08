'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle } from 'lucide-react';

// Set to true during development to show success even without parameters
// IMPORTANT: Set to false in production!
const TEST_MODE = process.env.NODE_ENV === 'development';

export default function Success() {
  const [loading, setLoading] = useState(true);
  const [paymentId, setPaymentId] = useState('');
  const [error, setError] = useState('');
  const [orderCompleted, setOrderCompleted] = useState(false);
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    console.log("Search params:", Object.fromEntries(searchParams.entries()));
    
    // First, try to get session_id from URL params
    const session_id = searchParams.get('session_id');
    
    // If we have a session_id in the URL, use that
    if (session_id) {
      console.log("Found session_id in URL:", session_id);
      handleSessionId(session_id);
    }
    // Test mode - simulate successful checkout
    else if (TEST_MODE) {
      console.log("🧪 TEST MODE ACTIVE: Simulating successful checkout");
      setPaymentId('pi_test_' + Math.random().toString(36).substring(2, 10));
      setOrderCompleted(true);
      setLoading(false);
    }
    // No payment information at all
    else {
      console.log("No payment parameters found in URL");
      setError("Missing payment information. Please return to checkout and try again.");
      setLoading(false);
    }
  }, [searchParams]);

  // Helper function to handle session ID
  const handleSessionId = (session_id) => {
    console.log("Handling session ID:", session_id);
    
    // First, get payment intent from Stripe
    fetch(`http://localhost:5000/checkout-session?session_id=${session_id}`)
      .then(response => {
        console.log("Session lookup response status:", response.status);
        if (!response.ok) {
          throw new Error(`Failed to fetch session (status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Session data from Stripe:", data);
        
        if (data.payment_intent) {
          setPaymentId(data.payment_intent);
          // Then, complete the order with the session ID
          completeOrderWithSession(session_id, data.payment_intent);
        } else {
          throw new Error("No payment intent found in session");
        }
      })
      .catch(err => {
        console.error("Error fetching session details:", err);
        setError("Failed to fetch payment details: " + err.message);
        setLoading(false);
      });
  };

  // Function to complete order using session ID - will fetch data from our backend
  const completeOrderWithSession = (session_id, payment_intent) => {
    console.log(`Completing order with session ID: ${session_id}`);
    
    // Call our final_purchase endpoint, which will retrieve the session data
    fetch('http://localhost:5008/final_purchase', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: session_id
      }),
    })
    .then(response => {
      console.log("final_purchase response status:", response.status);
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log("final_purchase response data:", data);
      if (data.code === 200) {
        setOrderCompleted(true);
      } else {
        throw new Error(data.message || "Order completion failed");
      }
    })
    .catch(err => {
      console.error("Error completing order:", err);
      setError("Failed to complete your order: " + err.message);
    })
    .finally(() => {
      setLoading(false);
    });
  };

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 bg-gray-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        {loading ? (
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="h-12 w-12 animate-spin text-blue-500 mb-4" />
            <p className="text-white">Finalizing your order...</p>
          </div>
        ) : error ? (
          <div className="text-red-500">
            <div className="text-3xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold mb-2">An error occurred</h2>
            <p>{error}</p>
            <div className="mt-4 space-y-2">
              <Button 
                className="w-full"
                onClick={() => router.push('/checkout')}
              >
                Return to Checkout
              </Button>
              
              {TEST_MODE && (
                <Button 
                  className="w-full mt-2"
                  variant="outline"
                  onClick={() => {
                    const testSessionId = 'cs_test_' + Math.random().toString(36).substring(2, 10);
                    console.log("Testing with session ID:", testSessionId);
                    window.location.href = `/success?session_id=${testSessionId}`;
                  }}
                >
                  Test with Random Session ID
                </Button>
              )}
            </div>
          </div>
        ) : (
          <>
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-center text-2xl font-bold tracking-tight text-white">
              Payment Successful!
            </h2>
            <p className="mt-2 text-gray-300">
              Thank you for your purchase. Your PC order has been confirmed.
            </p>
            {paymentId && (
              <div className="mt-4 p-4 bg-gray-800 rounded-md text-left">
                <p className="text-sm text-gray-400">Payment ID:</p>
                <p className="font-mono text-xs text-white break-all">{paymentId}</p>
              </div>
            )}
            <div className="mt-6">
              <Button
                className="w-full"
                onClick={() => router.push('/orders')}
              >
                View My Orders
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}