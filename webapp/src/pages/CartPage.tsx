
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

export default function CartPage() {
    const { cart, removeFromCart, updateQuantity, getCartTotal } = useCart();
    const { user } = useAuth();
    const navigate = useNavigate();

    const handleCheckout = () => {
        if (!user) {
            // Redirect to login with return URL
            navigate('/login?redirect=/checkout');
        } else {
            navigate('/checkout');
        }
    };

    if (cart.length === 0) {
        return (
            <div className="min-h-screen bg-gray-900 py-12">
                <div className="container mx-auto px-4">
                    <div className="max-w-2xl mx-auto text-center">
                        <svg className="w-24 h-24 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                        <h2 className="text-2xl font-bold text-white mb-4">Your Cart is Empty</h2>
                        <p className="text-gray-400 mb-8">
                            Looks like you haven't added any quantum-secure products yet!
                        </p>
                        <Link
                            to="/"
                            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Continue Shopping
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 py-12">
            <div className="container mx-auto px-4">
                <h1 className="text-3xl font-bold text-white mb-8">Shopping Cart</h1>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Cart Items */}
                    <div className="lg:col-span-2">
                        <div className="bg-gray-800 rounded-lg p-6">
                            {cart.map((item) => (
                                <div key={item.id} className="flex items-center gap-4 py-4 border-b border-gray-700 last:border-0">
                                    <img
                                        src={item.image}
                                        alt={item.name}
                                        className="w-24 h-24 object-cover rounded-lg"
                                    />

                                    <div className="flex-1">
                                        <h3 className="text-white font-semibold">{item.name}</h3>
                                        <p className="text-gray-400 text-sm">{item.description}</p>

                                        <div className="flex items-center gap-4 mt-2">
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                                                    className="w-8 h-8 bg-gray-700 text-white rounded flex items-center justify-center hover:bg-gray-600"
                                                >
                                                    -
                                                </button>
                                                <span className="text-white w-8 text-center">{item.quantity}</span>
                                                <button
                                                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                                    className="w-8 h-8 bg-gray-700 text-white rounded flex items-center justify-center hover:bg-gray-600"
                                                >
                                                    +
                                                </button>
                                            </div>

                                            <button
                                                onClick={() => removeFromCart(item.id)}
                                                className="text-red-400 hover:text-red-300 text-sm"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                    </div>

                                    <div className="text-right">
                                        <p className="text-white font-semibold">
                                            ${(item.price * item.quantity).toFixed(2)}
                                        </p>
                                        <p className="text-gray-400 text-sm">
                                            ${item.price.toFixed(2)} each
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Order Summary */}
                    <div className="lg:col-span-1">
                        <div className="bg-gray-800 rounded-lg p-6 sticky top-4">
                            <h2 className="text-xl font-semibold text-white mb-4">Order Summary</h2>

                            <div className="space-y-2 mb-4">
                                <div className="flex justify-between text-gray-400">
                                    <span>Subtotal</span>
                                    <span>${getCartTotal().toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                    <span>Quantum Security Fee</span>
                                    <span className="text-green-400">FREE</span>
                                </div>
                                <div className="flex justify-between text-gray-400">
                                    <span>Estimated Tax</span>
                                    <span>${(getCartTotal() * 0.08).toFixed(2)}</span>
                                </div>
                            </div>

                            <div className="border-t border-gray-700 pt-4 mb-6">
                                <div className="flex justify-between text-white font-semibold text-lg">
                                    <span>Total</span>
                                    <span>${(getCartTotal() * 1.08).toFixed(2)}</span>
                                </div>
                            </div>

                            <button
                                onClick={handleCheckout}
                                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all"
                            >
                                {user ? 'Proceed to Checkout' : 'Login to Checkout'}
                            </button>

                            <div className="mt-4 p-4 bg-gray-700/50 rounded-lg">
                                <div className="flex items-center gap-2 text-green-400 mb-2">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                    </svg>
                                    <span className="font-semibold">Quantum-Safe Checkout</span>
                                </div>
                                <p className="text-gray-400 text-sm">
                                    Your payment will be encrypted with post-quantum cryptography
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}