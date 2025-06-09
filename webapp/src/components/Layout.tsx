
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';

export default function Layout() {
    const { user, logout } = useAuth();
    const { getCartItemsCount } = useCart();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="min-h-screen bg-gray-900">
            {/* Navigation */}
            <nav className="bg-gray-800 border-b border-gray-700">
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                                <span className="text-white font-bold text-xl">Q</span>
                            </div>
                            <span className="text-white font-semibold text-lg">Quantum Commerce</span>
                        </Link>

                        {/* Nav Links */}
                        <div className="flex items-center gap-6">
                            <Link to="/" className="text-gray-300 hover:text-white transition-colors">
                                Products
                            </Link>

                            {user && (
                                <Link to="/orders" className="text-gray-300 hover:text-white transition-colors">
                                    My Orders
                                </Link>
                            )}

                            {(user?.user_type === 'admin' || user?.is_admin) && (
                                <Link to="/admin" className="text-gray-300 hover:text-white transition-colors">
                                    Admin
                                </Link>
                            )}

                            {/* Cart */}
                            <Link to="/cart" className="relative text-gray-300 hover:text-white transition-colors">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                </svg>
                                {getCartItemsCount() > 0 && (
                                    <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                        {getCartItemsCount()}
                                    </span>
                                )}
                            </Link>

                            {/* User Menu */}
                            {user ? (
                                <div className="flex items-center gap-4">
                                    <span className="text-gray-400 text-sm">
                                        Hi, {user.name || user.username || user.email.split('@')[0]}
                                    </span>
                                    <button
                                        onClick={handleLogout}
                                        className="text-gray-300 hover:text-white transition-colors"
                                    >
                                        Logout
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-center gap-4">
                                    <Link
                                        to="/login"
                                        className="text-gray-300 hover:text-white transition-colors"
                                    >
                                        Login
                                    </Link>
                                    <Link
                                        to="/register"
                                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                                    >
                                        Sign Up
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main>
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="bg-gray-800 border-t border-gray-700 mt-16">
                <div className="container mx-auto px-4 py-8">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <div>
                            <h3 className="text-white font-semibold mb-4">About Quantum Commerce</h3>
                            <p className="text-gray-400 text-sm">
                                The world's first e-commerce platform secured with post-quantum cryptography.
                            </p>
                        </div>

                        <div>
                            <h3 className="text-white font-semibold mb-4">Security Features</h3>
                            <ul className="text-gray-400 text-sm space-y-2">
                                <li>• CRYSTALS-Dilithium Signatures</li>
                                <li>• Identity-Based Encryption</li>
                                <li>• Quantum-Safe Protocols</li>
                                <li>• End-to-End Encryption</li>
                            </ul>
                        </div>

                        <div>
                            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
                            <ul className="text-gray-400 text-sm space-y-2">
                                <li><Link to="/" className="hover:text-white">Products</Link></li>
                                <li><Link to="/cart" className="hover:text-white">Cart</Link></li>
                                <li><Link to="/orders" className="hover:text-white">Orders</Link></li>
                                <li><a href="/api/docs" target="_blank" className="hover:text-white">API Docs</a></li>
                            </ul>
                        </div>

                        <div>
                            <h3 className="text-white font-semibold mb-4">Contact</h3>
                            <p className="text-gray-400 text-sm">
                                Email: support@quantumcommerce.com<br />
                                Phone: 1-800-QUANTUM<br />
                                Address: 123 Crypto St, Quantum City
                            </p>
                        </div>
                    </div>

                    <div className="border-t border-gray-700 mt-8 pt-8 text-center">
                        <p className="text-gray-400 text-sm">
                            © 2024 Quantum Commerce. Protected by post-quantum cryptography.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}