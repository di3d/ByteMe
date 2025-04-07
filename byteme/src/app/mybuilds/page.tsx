"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import BuildCard from "@/components/BuildCard";
import { useAuth } from "@/lib/auth-context";

export default function MyBuilds() {
    const { user, loading: authLoading } = useAuth(); // Use the loading state from useAuth
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
  
    useEffect(() => {
      if (authLoading) {
        return; // Skip data fetching while waiting for the auth state to be determined
      }
  
      if (!user) {
        setError("User is not logged in");
        setLoading(false);
        return;
      }
  
      const fetchData = async () => {
        const options = {
          method: "GET",
          url: `http://localhost:8000/recommendation-route/recommendation/customer/${user.uid}`,
        };
  
        try {
          const response = await axios.request(options);
          setData(response.data);
        } catch (error: unknown) {
          // Handle errors
          if (error instanceof Error) {
            setError(error.message);
          } else {
            setError("An unexpected error occurred");
          }
        } finally {
          setLoading(false);
        }
      };
  
      fetchData();
    }, [user, authLoading]); // Dependency on both `user` and `authLoading`
  
    if (authLoading) return <div>Loading authentication...</div>; // Show a loading message for auth state
    if (loading) return <div>Loading recommendations...</div>;
    if (error) return <div>Error: {error}</div>;

  return (
    <div className="container mx-auto px-4 py-8 min-h-screen text-white">
      <div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-12 px-6 rounded-xl mb-8">
        <h1 className="text-4xl font-extrabold mb-4">My Builds</h1>
        <p className="text-lg">
          Browse your builds or previously saved builds here
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.data.map((rec) => (
          <BuildCard
            key={rec.recommendation_id}
            title={rec.name}
            totalPrice={rec.cost}
            infoRows={rec.parts_list}
            showSaveButton={false}
          />
        ))}
      </div>
    </div>
  );
}
