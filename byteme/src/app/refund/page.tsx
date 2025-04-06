'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function RefundPage() {
  const [loading, setLoading] = useState(false);
  const [paymentId, setPaymentId] = useState('');
  const { user } = useAuth();
  const searchParams = useSearchParams();

  useEffect(() => {
    const paymentIntent = searchParams.get('payment_intent');
    if (paymentIntent) {
      setPaymentId(paymentIntent);
    }
  }, [searchParams]);

  const handleRefund = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Use environment variable or fallback to localhost
      const apiUrl = process.env.NEXT_PUBLIC_SCENARIO3_API_URL || 'http://127.0.0.1:5006';
      
      const refundResponse = await fetch(`${apiUrl}/initiate-refund`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_intent_id: paymentId,
          customer_email: user?.email
        }),
      });

      const data = await refundResponse.json();

      if (!refundResponse.ok) {
        throw new Error(data.error || 'Failed to process refund');
      }

      if (data.success) {
        toast.success('Refund Initiated', {
          description: 'Your refund request is being processed. You will receive a confirmation email shortly.',
        });
        setPaymentId(''); // Clear form
      } else {
        toast.error('Refund Failed', {
          description: data.error || 'Failed to process refund',
        });
      }
    } catch (error) {
      console.error('Refund Error:', error);
      toast.error('Refund Failed', {
        description: error instanceof Error ? error.message : 'An error occurred while processing your refund',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-md p-6">
      <Card>
        <CardHeader>
          <CardTitle>Process Full Refund</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRefund} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="paymentId">Payment Intent ID</Label>
              <Input
                id="paymentId"
                type="text"
                placeholder="Enter payment intent ID (pi_...)"
                value={paymentId}
                onChange={(e) => setPaymentId(e.target.value)}
                className="text-white placeholder:text-gray-400"
                required
              />
            </div>

            <div className="text-sm text-gray-500 mb-4">
              <p>Refund confirmation will be sent to: {user?.email}</p>
              <p className="mt-1 text-xs">Note: This will process a full refund for the entire transaction.</p>
            </div>
            
            <Button 
              type="submit" 
              className="w-full"
              disabled={loading}
              variant="default"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-white"></div>
                  <span>Processing Refund...</span>
                </div>
              ) : (
                'Process Full Refund'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}