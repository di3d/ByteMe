"use client";

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { AlertCircle, CheckCircle, Clock, ShoppingCart } from "lucide-react";
import { getAuth } from "firebase/auth";
import { format, parseISO, differenceInDays } from 'date-fns';

// Types
interface Order {
    order_id: string;
    customer_id: string;
    parts_list: string[];
    status: string;
    timestamp: string;
}

interface ComponentDetails {
    Id: number;
    Name: string;
    Price: number;
    Stock: number;
    ImageUrl: string;
    CategoryId: number;
}

export default function OrderDetailsPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const auth = getAuth();
    const [order, setOrder] = useState<Order | null>(null);
    const [components, setComponents] = useState<ComponentDetails[]>([]);
    const [loading, setLoading] = useState(true);
    const [isRefundable, setIsRefundable] = useState(false);
    const [processingRefund, setProcessingRefund] = useState(false);

    const orderId = searchParams.get('id');

    useEffect(() => {
        if (!auth.currentUser) {
            router.push('/login');
            return;
        }

        const fetchOrderDetails = async () => {
            try {
                // Fetch order details
                const orderResponse = await fetch(`http://localhost:5002/order/${orderId}`);

                if (!orderResponse.ok) {
                    throw new Error('Failed to fetch order details');
                }

                const orderData = await orderResponse.json();

                if (orderData.code !== 200) {
                    throw new Error(orderData.message || 'Failed to fetch order details');
                }

                // Check if order belongs to current user
                if (orderData.data.customer_id !== auth.currentUser?.uid) {
                    router.push('/orders');
                    return;
                }

                setOrder(orderData.data);

                // Check refund eligibility (within 30 days and not already refunded)
                const orderDate = parseISO(orderData.data.timestamp);
                const daysSinceOrder = differenceInDays(new Date(), orderDate);
                setIsRefundable(daysSinceOrder <= 30 && orderData.data.status !== 'refunded');

                // Handle parts list - could be a JSON string or already an array
                let partIds = orderData.data.parts_list;
                if (typeof partIds === 'string') {
                    try {
                        partIds = JSON.parse(partIds);
                    } catch (e) {
                        console.error("Error parsing parts_list:", e);
                        partIds = [];
                    }
                }

                const fetchedComponents: ComponentDetails[] = [];

                await Promise.all(
                    partIds.map(async (partId: string) => {
                        try {
                            const componentResponse = await fetch(
                                `https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById?ComponentId=${partId}`
                            );
                            
                            if (!componentResponse.ok) {
                                console.error(`Failed to fetch component ${partId}`);
                                return;
                            }
                            
                            const componentData: ComponentDetails = await componentResponse.json();
                            fetchedComponents.push(componentData);
                        } catch (error) {
                            console.error(`Error fetching component ${partId}:`, error);
                        }
                    })
                );
                
                // Sort components by category ID for a nice display
                fetchedComponents.sort((a, b) => a.CategoryId - b.CategoryId);
                setComponents(fetchedComponents);
            } catch (error) {
                console.error("Error fetching order details:", error);
                toast.error("Failed to load order details");
            } finally {
                setLoading(false);
            }
        };

        fetchOrderDetails();
    }, [orderId, router, auth.currentUser]);

    const handleRefundRequest = async () => {
        if (!order || !isRefundable) return;
        
        setProcessingRefund(true);
        
        try {
            const response = await fetch('http://localhost:5006/initiate-refund', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    order_id: order.order_id,
                    customer_id: order.customer_id,
                }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                toast.success('Refund processed successfully');
                // Update the order status locally
                setOrder({ ...order, status: 'refunded' });
                setIsRefundable(false);
            } else {
                throw new Error(data.error || 'Failed to process refund');
            }
        } catch (error) {
            console.error('Error processing refund:', error);
            toast.error('Failed to process refund request');
        } finally {
            setProcessingRefund(false);
        }
    };

    if (loading) {
        return (
            <div className="container mx-auto p-4 py-8">
                <div className="flex justify-center items-center h-64">
                    <p className="text-lg">Loading order details...</p>
                </div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="container mx-auto p-4 py-8">
                <div className="flex justify-center items-center h-64">
                    <p className="text-lg text-red-500">Order not found</p>
                </div>
            </div>
        );
    }

    const orderDate = parseISO(order.timestamp);
    const totalPrice = components.reduce((sum, component) => sum + component.Price, 0);

    return (
        <div className="container mx-auto p-4 py-8">
            <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold">Order Details</h1>
                    <p className="text-muted-foreground">
                        Placed on {format(orderDate, 'MMMM d, yyyy')} at {format(orderDate, 'h:mm a')}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <StatusBadge status={order.status} />
                    <span className="font-medium">Order #{order.order_id.substring(0, 8)}</span>
                </div>
            </div>

            <Card className="mb-8">
                <CardHeader>
                    <CardTitle>Order Summary</CardTitle>
                    <CardDescription>Overview of your order</CardDescription>
                </CardHeader>

                <CardContent>
                    <div className="grid gap-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <h3 className="font-medium text-sm text-muted-foreground">Order Number</h3>
                                <p>{order.order_id}</p>
                            </div>
                            <div>
                                <h3 className="font-medium text-sm text-muted-foreground">Order Date</h3>
                                <p>{format(orderDate, 'MMMM d, yyyy')}</p>
                            </div>
                            <div>
                                <h3 className="font-medium text-sm text-muted-foreground">Status</h3>
                                <StatusBadge status={order.status} />
                            </div>
                            <div>
                                <h3 className="font-medium text-sm text-muted-foreground">Total</h3>
                                <p className="font-bold">${totalPrice.toFixed(2)}</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <h2 className="text-xl font-bold mb-4">Ordered Components</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {components.map((component) => {
                    // Map the categories based on CategoryId
                    const categoryMap: Record<number, string> = {
                        1: 'CPU',
                        2: 'GPU',
                        3: 'Motherboard',
                        4: 'RAM',
                        5: 'Storage',
                        6: 'Case',
                        7: 'PSU',
                        8: 'Cooling',
                    };
                    const category = categoryMap[component.CategoryId] || 'Other';
                    
                    return (
                        <Card key={component.Id} className="overflow-hidden">
                            <div className="h-40 bg-slate-100 flex items-center justify-center">
                                {component.ImageUrl ? (
                                    <img
                                        src={component.ImageUrl}
                                        alt={component.Name}
                                        className="h-full w-full object-cover"
                                    />
                                ) : (
                                    <div className="text-slate-400 flex flex-col items-center">
                                        <ShoppingCart size={36} />
                                        <span className="text-sm mt-2">No image</span>
                                    </div>
                                )}
                            </div>

                            <CardHeader className="pb-2">
                                <CardTitle className="text-lg">{component.Name}</CardTitle>
                                <CardDescription>{category}</CardDescription>
                            </CardHeader>

                            <CardFooter className="pt-0 flex justify-between">
                                <span className="font-bold">${component.Price.toFixed(2)}</span>
                                <Badge variant="outline">Component #{component.Id}</Badge>
                            </CardFooter>
                        </Card>
                    );
                })}
            </div>

            <Separator className="my-8" />

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-xl font-bold">Total: ${totalPrice.toFixed(2)}</h2>
                    <p className="text-sm text-muted-foreground">
                        {components.length} item{components.length !== 1 ? 's' : ''}
                    </p>
                </div>

                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={() => router.push('/orders')}
                    >
                        Back to Orders
                    </Button>

                    {isRefundable && (
                        <Button
                            variant="destructive"
                            onClick={handleRefundRequest}
                            disabled={processingRefund}
                        >
                            {processingRefund ? "Processing..." : "Request Refund"}
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
}

// Helper component to display order status
function StatusBadge({ status }: { status: string }) {
    switch (status.toLowerCase()) {
        case 'completed':
            return (
                <Badge className="bg-green-100 text-green-800 hover:bg-green-100" variant="outline">
                    <CheckCircle className="mr-1" size={14} /> Completed
                </Badge>
            );
        case 'processing':
            return (
                <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100" variant="outline">
                    <Clock className="mr-1" size={14} /> Processing
                </Badge>
            );
        case 'refunded':
            return (
                <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100" variant="outline">
                    <AlertCircle className="mr-1" size={14} /> Refunded
                </Badge>
            );
        case 'refund_pending':
            return (
                <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100" variant="outline">
                    <Clock className="mr-1" size={14} /> Refund Pending
                </Badge>
            );
        case 'pending':
        default:
            return (
                <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100" variant="outline">
                    <Clock className="mr-1" size={14} /> Pending
                </Badge>
            );
    }
}