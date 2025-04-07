'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
    
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

    const calculateTotal = (partsList: any[]) => {
        return partsList.reduce((total, part) => total + (part.price || 0), 0);
    };

    if (loading) {
        return (
            <div className="p-4">
                <p>Loading your orders...</p>
                {/* Consider adding a loading spinner here */}
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-red-500">
                <p>Error: {error}</p>
                <button onClick={fetchOrders} className="mt-2 p-2 bg-blue-500 text-white rounded">
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">My Orders</h1>
            {orders.length === 0 ? (
                <p>You have no orders yet.</p>
            ) : (
                <div className="space-y-4">
                    {orders.map((order) => (
                        <div
                            key={order.order_id}
                            className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow"
                        >
                            <div className="flex justify-between items-center">
                                <div>
                                    <p><strong>Order ID:</strong> {order.order_id}</p>
                                    <p><strong>Status:</strong> {order.status}</p>
                                    <p><strong>Date:</strong> {new Date(order.timestamp).toLocaleDateString()}</p>
                                    <p><strong>Total:</strong> ${calculateTotal(order.parts_list).toFixed(2)}</p>
                                </div>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => router.push(`/orderDetails?id=${order.order_id}`)}
                                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                                    >
                                        View Details
                                    </button>
                                    {/* Conditionally render refund button based on order eligibility */}
                                    {/* Example condition - you'd replace with actual refund eligibility logic */}
                                    {new Date(order.timestamp) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) && (
                                        <button
                                            onClick={() => router.push(`/refund/${order.order_id}`)}
                                            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                                        >
                                            Refund
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MyOrdersPage;