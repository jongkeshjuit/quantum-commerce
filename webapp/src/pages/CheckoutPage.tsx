import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function CheckoutPage() {
    const navigate = useNavigate();
    const { cart, getCartTotal, clearCart } = useCart();
    const { token } = useAuth();
    const [loading, setLoading] = useState(false);
    const [paymentStatus, setPaymentStatus] = useState<any>(null);

    const [formData, setFormData] = useState({
        cardNumber: '',
        expMonth: '',
        expYear: '',
        cvv: '',
        billingName: '',
        billingAddress: '',
        billingCity: '',
        billingState: '',
        billingZip: ''
    });

    const formatCardNumber = (value: string) => {
        const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        const matches = v.match(/\d{4,16}/g);
        const match = (matches && matches[0]) || '';
        const parts = [];

        for (let i = 0, len = match.length; i < len; i += 4) {
            parts.push(match.substring(i, i + 4));
        }

        return parts.length ? parts.join(' ') : value;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setPaymentStatus(null);

        try {
            const response = await axios.post(
                `${API_URL}/api/payments/process`,
                {
                    amount: getCartTotal() * 1.08, // Including tax
                    currency: 'USD',
                    payment_method: 'credit_card',
                    card_data: {
                        number: formData.cardNumber.replace(/\s/g, ''),
                        exp_month: formData.expMonth,
                        exp_year: formData.expYear,
                        cvv: formData.cvv
                    },
                    billing_address: {
                        name: formData.billingName,
                        street: formData.billingAddress,
                        city: formData.billingCity,
                        state: formData.billingState,
                        zip: formData.billingZip
                    },
                    items: cart.map(item => ({
                        id: item.id,
                        name: item.name,
                        price: item.price,
                        quantity: item.quantity
                    }))
                },
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            if (response.data.status === 'completed') {
                setPaymentStatus({
                    success: true,
                    ...response.data
                });

                // Clear cart and redirect after 3 seconds
                clearCart();
                setTimeout(() => {
                    navigate(`/order-success/${response.data.transaction_id}`);
                }, 3000);
            }
        } catch (error: any) {
            setPaymentStatus({
                success: false,
                message: error.response?.data?.detail || 'Payment failed'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;

        if (name === 'cardNumber') {
            setFormData({ ...formData, [name]: formatCardNumber(value) });
        } else {
            setFormData({ ...formData, [name]: value });
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 py-12">
            <div className="container mx-auto px-4">
                <h1 className="text-3xl font-bold text-white mb-8">Secure Checkout</h1>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Payment Form */}
                    <div>
                        <div className="bg-gray-800 rounded-lg p-6">
                            <h2 className="text-xl font-semibold text-white mb-6">Payment Information</h2>

                            {/* Security Badge */}
                            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 mb-6">
                                <div className="flex items-center gap-3">
                                    <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                    </svg>
                                    <div>
                                        <p className="text-green-400 font-semibold">Quantum-Safe Transaction</p>
                                        <p className="text-green-300 text-sm">
                                            Protected by CRYSTALS-Dilithium digital signatures
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/* Card Number */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Card Number
                                    </label>
                                    <input
                                        type="text"
                                        name="cardNumber"
                                        value={formData.cardNumber}
                                        onChange={handleInputChange}
                                        placeholder="1234 5678 9012 3456"
                                        maxLength={19}
                                        required
                                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                    />
                                </div>

                                {/* Expiry and CVV */}
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Month
                                        </label>
                                        <input
                                            type="text"
                                            name="expMonth"
                                            value={formData.expMonth}
                                            onChange={handleInputChange}
                                            placeholder="MM"
                                            maxLength={2}
                                            required
                                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Year
                                        </label>
                                        <input
                                            type="text"
                                            name="expYear"
                                            value={formData.expYear}
                                            onChange={handleInputChange}
                                            placeholder="YYYY"
                                            maxLength={4}
                                            required
                                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            CVV
                                        </label>
                                        <input
                                            type="text"
                                            name="cvv"
                                            value={formData.cvv}
                                            onChange={handleInputChange}
                                            placeholder="123"
                                            maxLength={3}
                                            required
                                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                </div>

                                {/* Billing Info */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Name on Card
                                    </label>
                                    <input
                                        type="text"
                                        name="billingName"
                                        value={formData.billingName}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Billing Address
                                    </label>
                                    <input
                                        type="text"
                                        name="billingAddress"
                                        value={formData.billingAddress}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                    />
                                </div>

                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            City
                                        </label>
                                        <input
                                            type="text"
                                            name="billingCity"
                                            value={formData.billingCity}
                                            onChange={handleInputChange}
                                            required
                                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            State
                                        </label>
                                        <input
                                            type="text"
                                            name="billingState"
                                            value={formData.billingState}
                                            onChange={handleInputChange}
                                            maxLength={2}
                                            required
                                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            ZIP
                                        </label>
                                        <input
                                            type="text"
                                            name="billingZip"
                                            value={formData.billingZip}
                                            onChange={handleInputChange}
                                            maxLength={5}
                                            required
                                            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-60"
                                >
                                    {loading ? 'Processing...' : `Pay $${(getCartTotal() * 1.08).toFixed(2)}`}
                                </button>
                            </form>

                            {/* Payment Status */}
                            {paymentStatus && (
                                <div className={`mt-6 p-4 rounded-lg ${paymentStatus.success
                                        ? 'bg-green-900/20 border border-green-500/30'
                                        : 'bg-red-900/20 border border-red-500/30'
                                    }`}>
                                    {paymentStatus.success ? (
                                        <div>
                                            <p className="text-green-400 font-semibold mb-2">
                                                ✅ Payment Successful!
                                            </p>
                                            <p className="text-gray-300 text-sm">
                                                Transaction ID: {paymentStatus.transaction_id}
                                            </p>
                                            <p className="text-gray-400 text-sm mt-2">
                                                Redirecting to order confirmation...
                                            </p>
                                        </div>
                                    ) : (
                                        <p className="text-red-400">{paymentStatus.message}</p>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Order Summary */}
                    <div>
                        <div className="bg-gray-800 rounded-lg p-6">
                            <h2 className="text-xl font-semibold text-white mb-6">Order Summary</h2>

                            {/* Items */}
                            <div className="space-y-4 mb-6">
                                {cart.map((item) => (
                                    <div key={item.id} className="flex items-center gap-4">
                                        <img
                                            src={item.image}
                                            alt={item.name}
                                            className="w-16 h-16 object-cover rounded-lg"
                                        />
                                        <div className="flex-1">
                                            <h4 className="text-white font-medium">{item.name}</h4>
                                            <p className="text-gray-400 text-sm">Qty: {item.quantity}</p>
                                        </div>
                                        <p className="text-white">
                                            ${(item.price * item.quantity).toFixed(2)}
                                        </p>
                                    </div>
                                ))}
                            </div>

                            {/* Totals */}
                            <div className="border-t border-gray-700 pt-4 space-y-2">
                                <div className="flex justify-between text-gray-400">
                                    <span>Subtotal</span>
                                    <span>${getCartTotal().toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                    <span>Tax (8%)</span>
                                    <span>${(getCartTotal() * 0.08).toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                    <span>Quantum Security</span>
                                    <span className="text-green-400">FREE</span>
                                </div>
                                <div className="border-t border-gray-700 pt-2">
                                    <div className="flex justify-between text-white font-semibold text-lg">
                                        <span>Total</span>
                                        <span>${(getCartTotal() * 1.08).toFixed(2)}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Security Info */}
                            <div className="mt-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                                <h3 className="text-blue-400 font-semibold mb-2">
                                    Your Security Matters
                                </h3>
                                <ul className="text-blue-300 text-sm space-y-1">
                                    <li>• Payment encrypted with IBE</li>
                                    <li>• Transaction signed with Dilithium</li>
                                    <li>• Quantum-resistant protection</li>
                                    <li>• End-to-end encryption</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}