"use client"

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AccountSetupPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [address, setAddress] = useState("");
  
  useEffect(() => {
    // Redirect to home if no user
    if (!user && !loading) {
      router.push('/login');
      return;
    }
    
    // Check if user already has an address
    const checkUserAddress = async () => {
      try {
        if (!user?.uid) return;
        
        const response = await fetch(`http://localhost:8000/customer/${user.uid}`);
        const data = await response.json();
        
        // If user has valid address, redirect to home
        if (data.code === 200 && data.data.address && data.data.address !== "Not provided") {
          router.push('/');
        }
      } catch (error) {
        console.error("Error checking user address:", error);
      }
    };
    
    checkUserAddress();
  }, [user, router]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!address.trim()) {
      toast.error("Please enter your address");
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/customer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: user?.uid,
          name: user?.displayName || "Unknown",
          email: user?.email,
          address: address
        }),
      });
      
      const data = await response.json();
      
      if (data.code === 201 || data.code === 200 || data.code === 409) {
        toast.success("Address saved successfully!");
        router.push('/');
      } else {
        throw new Error(data.message || "Failed to save address");
      }
    } catch (error) {
      console.error("Error saving address:", error);
      toast.error("Failed to save your address. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-800 to-purple-800 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Complete Your Account</CardTitle>
          <p className="text-muted-foreground mt-2">
            Please provide your shipping address to continue
          </p>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="address" className="text-sm font-medium">
                Your Address
              </label>
              <Textarea
                id="address"
                placeholder="123 Main Street, City, Country, Postal Code"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                required
                className="min-h-24"
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Address"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}