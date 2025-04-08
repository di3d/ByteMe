'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { DateTime } from 'luxon';

interface Order {
    order_id: string;
    status: string;
    timestamp: string;
    parts_list: any[]; // Adjust type as needed
}

const MyOrdersPage = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    // Fetch orders for the logged-in user
    const fetchOrders = async () => {
        try {
            const userId = localStorage.getItem('user_id');
            if (!userId) {
                throw new Error('User not logged in');
            }

            const response = await fetch(`http://localhost:5002/order/customers/${userId}`);

            if (!response.ok) {
                throw new Error('Failed to fetch orders');
            }

            const data = await response.json();
            setOrders(data.data || []);
            setError(null);
        } catch (error) {
            console.error('Error fetching orders:', error);
            setError(error instanceof Error ? error.message : 'An unknown error occurred');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);


// Simplified formatDateTime function for Singapore time

const formatDateTime = (timestamp: string) => {
    try {
        // Parse the timestamp in UTC
        const dt = DateTime.fromISO(timestamp, { zone: 'utc' });
        
        // Convert to Singapore time
        const sgt = dt.setZone('Asia/Singapore');
        
        // Debug
        console.log({
            originalTimestamp: timestamp,
            luxonUTC: dt.toString(),
            luxonSGT: sgt.toString(),
        });
        
        return {
            date: sgt.toFormat('LLL d, yyyy'),
            time: sgt.toFormat('h:mm a') + ' (SGT)'
        };
    } catch (error) {
        console.error("Error formatting date:", error);
        return { date: "Error", time: "Error" };
    }
};

    // Function to get status badge color for dark theme
    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'completed':
                return 'bg-green-900 text-green-300';
            case 'refunded':
                return 'bg-red-900 text-red-300';
            case 'pending':
                return 'bg-yellow-900 text-yellow-300';
            case 'processing':
                return 'bg-blue-900 text-blue-300';
            default:
                return 'bg-gray-800 text-gray-300';
        }
    };

    if (loading) {
        return (
            <div className="p-4 text-white">
                <p>Loading your orders...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-red-400">
                <p>Error: {error}</p>
                <button onClick={fetchOrders} className="mt-2 p-2 bg-blue-600 text-white rounded">
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="p-4 max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-6 text-white">My Orders</h1>
            
            {orders.length === 0 ? (
                <div className="text-center p-8 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="text-gray-400">You have no orders yet.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {orders.map((order) => {
                        const { date, time } = formatDateTime(order.timestamp);
                        const statusClass = getStatusColor(order.status);
                        
                        return (
                            <Card key={order.order_id} className="bg-gray-800 border-gray-700 hover:bg-gray-750 transition-colors">
                                <CardContent className="p-6">
                                    <div className="flex justify-between items-start">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2 mb-2">
                                                <h3 className="font-semibold text-white">Order #{order.order_id.slice(-8)}</h3>
                                                <Badge className={`${statusClass}`}>
                                                    {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                                                </Badge>
                                            </div>
                                            
                                            <div className="text-sm text-gray-400 space-y-1">
                                                <p className="font-mono text-xs text-gray-500 truncate max-w-xs">
                                                    {order.order_id}
                                                </p>
                                                <p>
                                                    <span className="inline-block w-16 font-medium text-gray-300">Date:</span> 
                                                    {date}
                                                </p>
                                                <p>
                                                    <span className="inline-block w-16 font-medium text-gray-300">Time:</span> 
                                                    {time}
                                                </p>
                                                <p>
                                                    <span className="inline-block w-16 font-medium text-gray-300">Items:</span> 
                                                    {order.parts_list.length} components
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                                
                                <CardFooter className="flex justify-end gap-2 p-4 bg-gray-850 border-t border-gray-700">
                                    <button
                                        onClick={() => router.push(`/orderDetails?id=${order.order_id}`)}
                                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                    >
                                        View Details
                                    </button>
                                    
                                    {new Date(order.timestamp) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) && 
                                     order.status !== 'refunded' && (
                                        <button
                                            onClick={() => router.push(`/refund?order_id=${order.order_id}`)}
                                            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                                        >
                                            Request Refund
                                        </button>
                                    )}
                                </CardFooter>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default MyOrdersPage;