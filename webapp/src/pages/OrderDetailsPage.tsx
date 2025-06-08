import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface OrderDetails {
    transaction_id: string;
    amount: number;
    currency: string;
    status: string;
    timestamp: string;
    items: Array<{
        name: string;
        price: number;
        quantity: number;
    }>;
    payment_method: string;
    billing_address?: {
        name: string;
        street: string;
        city: string;
        state: string;
        zip: string;
    };
    quantum_security: {
        ibe_encrypted: boolean;
        dilithium_signed: boolean;
        signature_verified: boolean;
    };
}

export default function OrderDetailsPage() {
    const { transactionId } = useParams<{ transactionId: string }>();
    const { token } = useAuth();
    const [orderDetails, setOrderDetails] = useState<OrderDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [verifying, setVerifying] = useState(false);

    useEffect(() => {
        if (transactionId) {
            fetchOrderDetails();
        }
    }, [transactionId]);

    const fetchOrderDetails = async () => {
        try {
            const response = await axios.get(
                `${API_URL}/api/orders/${transactionId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setOrderDetails(response.data);
        } catch (error) {
            console.error('Failed to fetch order details:', error);
        } finally {
            setLoading(false);
        }
    };

    const verifySignature = async () => {
        setVerifying(true);
        try {
            const response = await axios.post(
                `${API_URL}/api/payments/verify`,
                { transaction_id: transactionId },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            if (response.data.verified) {
                setOrderDetails(prev => prev ? {
                    ...prev,
                    quantum_security: {
                        ...prev.quantum_security,
                        signature_verified: true
                    }
                } : null);
                alert('✅ Signature verified successfully!');
            }
        } catch (error) {
            console.error('Verification failed:', error);
            alert('❌ Verification failed');
        } finally {
            setVerifying(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (!orderDetails) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-white mb-4">Order Not Found</h1>
                    <Link to="/orders" className="text-blue-400 hover:text-blue-300">
                        ← Back to Order History
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 py-12">
            <div className="container mx-auto px-4 max-w-4xl">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <Link to="/orders" className="text-blue-400 hover:text-blue-300 mb-2 inline-block">
                            ← Back to Order History
                        </Link>
                        <h1 className="text-3xl font-bold text-white">Order Details</h1>
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-gray-400">Transaction ID</div>
                        <div className="text-white font-mono">{orderDetails.transaction_id}</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Details */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Order Summary */}
                        <div className="bg-gray-800 rounded-lg p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Order Summary</h2>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-400">Date:</span>
                                    <div className="text-white">
                                        {new Date(orderDetails.timestamp).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </div>
                                </div>
                                <div>
                                    <span className="text-gray-400">Status:</span>
                                    <div>
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${orderDetails.status === 'completed'
                                                ? 'bg-green-900/20 text-green-400 border border-green-500/30'
                                                : 'bg-yellow-900/20 text-yellow-400 border border-yellow-500/30'
                                            }`}>
                                            {orderDetails.status}
                                        </span>
                                    </div>
                                </div>
                                <div>
                                    <span className="text-gray-400">Payment Method:</span>
                                    <div className="text-white capitalize">{orderDetails.payment_method}</div>
                                </div>
                                <div>
                                    <span className="text-gray-400">Total Amount:</span>
                                    <div className="text-white font-semibold">
                                        ${orderDetails.amount.toFixed(2)} {orderDetails.currency}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Items */}
                        <div className="bg-gray-800 rounded-lg p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Items Purchased</h2>
                            <div className="space-y-3">
                                {orderDetails.items.map((item, index) => (
                                    <div key={index} className="flex justify-between items-center py-3 border-b border-gray-700 last:border-b-0">
                                        <div>
                                            <h3 className="text-white font-medium">{item.name}</h3>
                                            <p className="text-gray-400 text-sm">Quantity: {item.quantity}</p>
                                        </div>
                                        <div className="text-white font-semibold">
                                            ${(item.price * item.quantity).toFixed(2)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="border-t border-gray-700 pt-3 mt-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-400">Subtotal:</span>
                                    <span className="text-white">${(orderDetails.amount / 1.08).toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-400">Tax (8%):</span>
                                    <span className="text-white">${(orderDetails.amount - orderDetails.amount / 1.08).toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between items-center text-lg font-semibold pt-2 border-t border-gray-700 mt-2">
                                    <span className="text-white">Total:</span>
                                    <span className="text-white">${orderDetails.amount.toFixed(2)} {orderDetails.currency}</span>
                                </div>
                            </div>
                        </div>

                        {/* Billing Address */}
                        {orderDetails.billing_address && (
                            <div className="bg-gray-800 rounded-lg p-6">
                                <h2 className="text-xl font-semibold text-white mb-4">Billing Address</h2>
                                <div className="text-gray-300">
                                    <div className="font-medium">{orderDetails.billing_address.name}</div>
                                    <div>{orderDetails.billing_address.street}</div>
                                    <div>
                                        {orderDetails.billing_address.city}, {orderDetails.billing_address.state} {orderDetails.billing_address.zip}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Security Sidebar */}
                    <div className="space-y-6">
                        {/* Quantum Security Status */}
                        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
                            <h2 className="text-blue-400 font-semibold mb-4 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                                Quantum Security
                            </h2>

                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-blue-200">IBE Encryption</span>
                                    <span className={`w-3 h-3 rounded-full ${orderDetails.quantum_security.ibe_encrypted ? 'bg-green-400' : 'bg-red-400'}`}></span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-blue-200">Dilithium Signed</span>
                                    <span className={`w-3 h-3 rounded-full ${orderDetails.quantum_security.dilithium_signed ? 'bg-green-400' : 'bg-red-400'}`}></span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-blue-200">Signature Verified</span>
                                    <span className={`w-3 h-3 rounded-full ${orderDetails.quantum_security.signature_verified ? 'bg-green-400' : 'bg-yellow-400'}`}></span>
                                </div>
                            </div>

                            <button
                                onClick={verifySignature}
                                disabled={verifying || orderDetails.quantum_security.signature_verified}
                                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors"
                            >
                                {verifying ? 'Verifying...' :
                                    orderDetails.quantum_security.signature_verified ? 'Verified ✓' :
                                        'Verify Signature'}
                            </button>
                        </div>

                        {/* Security Info */}
                        <div className="bg-gray-800 rounded-lg p-6">
                            <h3 className="text-white font-semibold mb-3">Security Features</h3>
                            <div className="space-y-3 text-sm">
                                <div className="flex items-start gap-3">
                                    <svg className="w-4 h-4 text-green-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg>
                                    <div>
                                        <p className="text-gray-300">Identity-Based Encryption</p>
                                        <p className="text-gray-500">Payment data encrypted with your unique identity key</p>
                                    </div>
                                </div>
                                <div className="flex items-start gap-3">
                                    <svg className="w-4 h-4 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                    </svg>
                                    <div>
                                        <p className="text-gray-300">Quantum-Resistant Signatures</p>
                                        <p className="text-gray-500">Transaction integrity protected against quantum attacks</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}