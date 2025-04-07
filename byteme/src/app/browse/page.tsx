"use client";

import { Key, useEffect, useState } from "react";
import axios from "axios";
import BuildCard from "@/components/BuildCard";

export default function Browse() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [data, setData] = useState<any>(null); // Use appropriate type instead of `any`
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const options = {
        method: "GET",
        url: "http://localhost:8000/recommendation-route/recommendation/all",
      };

      try {
        const response = await axios.request(options);
        setData(response.data);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); // Empty dependency array means this effect runs once when the component mounts

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="container mx-auto px-4 py-8 min-h-screen text-white">
      <div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-12 px-6 rounded-xl mb-8">
        <h1 className="text-4xl font-extrabold mb-4">Community PC Builder</h1>
        <p className="text-lg">
          Build your perfect PC with recommendations from our community of
          enthusiasts
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.data.map((rec: { recommendation_id: Key | null | undefined; name: string; cost: number; parts_list: number[]; }) => (
          <BuildCard
            key={rec.recommendation_id}
            title={rec.name}
            totalPrice={rec.cost}
            infoRows={rec.parts_list}
            showSaveButton={true}
          />
        ))}
      </div>
    </div>
  );
}
