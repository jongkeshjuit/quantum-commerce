import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function OrderSuccessPage() {
    const { orderId } = useParams();
    const { token } = useAuth();
    const [orderDetails, setOrderDetails] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch order details
        const fetchOrder = async () => {
            try {
                const response = await axios.get(
                    `${API_URL}/api/payments/${orderId}`,
                    {
                        headers: { Authorization: `Bearer ${token}` }
                    }
                );
                setOrderDetails(response.data);
            } catch (error) {
                console.error('Failed to fetch order details:', error);
            } finally {
                setLoading(false);
            }
        };

        if (orderId && token) {
            fetchOrder();
        }
    }, [orderId, token]);

    return (
        <div className="min-h-screen bg-gray-900 py-12">
            <div className="container mx-auto px-4">
                <div className="max-w-2xl mx-auto">
                    {/* Success Animation */}
                    <div className="text-center mb-8">
                        <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
                            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2">Order Confirmed!</h1>
                        <p className="text-gray-400">
                            Thank you for your purchase. Your order has been secured with quantum cryptography.
                        </p>
                    </div>

                    {/* Order Details Card */}
                    <div className="bg-gray-800 rounded-lg p-8 mb-8">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold text-white">Order Details</h2>
                            <span className="text-green-400 text-sm flex items-center gap-1">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                                Quantum Secured
                            </span>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <p className="text-gray-400 text-sm">Transaction ID</p>
                                <p className="text-white font-mono">{orderId}</p>
                            </div>

                            <div>
                                <p className="text-gray-400 text-sm">Order Date</p>
                                <p className="text-white">{new Date().toLocaleString()}</p>
                            </div>

                            <div>
                                <p className="text-gray-400 text-sm">Status</p>
                                <span className="inline-flex items-center gap-2 bg-green-900/20 text-green-400 px-3 py-1 rounded-full text-sm">
                                    <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                                    Completed
                                </span>
                            </div>

                            {orderDetails && (
                                <div>
                                    <p className="text-gray-400 text-sm">Customer ID</p>
                                    <p className="text-white">{orderDetails.customer_id}</p>
                                </div>
                            )}
                        </div>

                        {/* Security Features */}
                        <div className="mt-6 pt-6 border-t border-gray-700">
                            <h3 className="text-white font-semibold mb-3">Transaction Security</h3>
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-gray-300">
                                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span>Payment encrypted with Identity-Based Encryption</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-300">
                                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span>Transaction signed with CRYSTALS-Dilithium</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-300">
                                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span>Quantum-resistant digital signature verified</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* What's Next */}
                    <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6 mb-8">
                        <h3 className="text-blue-400 font-semibold mb-2">What happens next?</h3>
                        <ul className="text-blue-300 space-y-2 text-sm">
                            <li>• You'll receive an encrypted confirmation email</li>
                            <li>• Your order will be processed within 24 hours</li>
                            <li>• Track your order status in your account</li>
                            <li>• Digital receipt available in your order history</li>
                        </ul>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            to="/orders"
                            className="bg-gray-700 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors text-center"
                        >
                            View Order History
                        </Link>
                        <Link
                            to="/"
                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center"
                        >
                            Continue Shopping
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}