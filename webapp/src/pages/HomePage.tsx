import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import ProductCard from '../components/ProductCard';
import Hero from '../components/Hero';

// Mock products data - trong production sẽ lấy từ API
const MOCK_PRODUCTS = [
    {
        id: '1',
        name: 'Quantum-Safe Laptop',
        description: 'Laptop với mã hóa quantum-resistant built-in',
        price: 1299.99,
        image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
        category: 'Electronics',
        features: ['Post-Quantum Encryption', 'Secure Boot', 'Hardware Security Module']
    },
    {
        id: '2',
        name: 'Crypto Hardware Wallet',
        description: 'Hardware wallet với Dilithium signatures',
        price: 199.99,
        image: 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=500',
        category: 'Security',
        features: ['CRYSTALS-Dilithium', 'Quantum-Safe', 'USB-C']
    },
    {
        id: '3',
        name: 'Secure Smartphone',
        description: 'Smartphone với IBE encryption cho messages',
        price: 899.99,
        image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
        category: 'Electronics',
        features: ['IBE Messaging', 'Secure Enclave', '5G']
    },
    {
        id: '4',
        name: 'Privacy VPN Router',
        description: 'Router với post-quantum VPN protocols',
        price: 349.99,
        image: 'https://images.unsplash.com/photo-1606904825846-647eb07f5be2?w=500',
        category: 'Networking',
        features: ['Quantum-Safe VPN', 'WiFi 6E', 'Open Source']
    },
    {
        id: '5',
        name: 'Encrypted USB Drive',
        description: 'USB drive với hardware encryption',
        price: 89.99,
        image: 'https://images.unsplash.com/photo-1618478047375-2700c2f03456?w=500',
        category: 'Storage',
        features: ['256-bit AES', 'Biometric Lock', '1TB Storage']
    },
    {
        id: '6',
        name: 'Security Camera System',
        description: 'AI-powered camera với encrypted storage',
        price: 599.99,
        image: 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=500',
        category: 'Security',
        features: ['4K Resolution', 'Night Vision', 'Cloud Backup']
    }
];

const CATEGORIES = ['All', 'Electronics', 'Security', 'Networking', 'Storage'];

export default function HomePage() {
    const [products, setProducts] = useState(MOCK_PRODUCTS);
    const [filteredProducts, setFilteredProducts] = useState(MOCK_PRODUCTS);
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [searchTerm, setSearchTerm] = useState('');
    const { addToCart } = useCart();

    // Filter products
    useEffect(() => {
        let filtered = products;

        if (selectedCategory !== 'All') {
            filtered = filtered.filter(p => p.category === selectedCategory);
        }

        if (searchTerm) {
            filtered = filtered.filter(p =>
                p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                p.description.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        setFilteredProducts(filtered);
    }, [selectedCategory, searchTerm, products]);

    return (
        <div className="min-h-screen bg-gray-900">
            {/* Hero Section */}
            <Hero />

            {/* Search and Filter */}
            <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col md:flex-row gap-4 mb-8">
                    {/* Search */}
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search products..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                        />
                    </div>

                    {/* Category Filter */}
                    <div className="flex gap-2">
                        {CATEGORIES.map(category => (
                            <button
                                key={category}
                                onClick={() => setSelectedCategory(category)}
                                className={`px-4 py-2 rounded-lg transition-all ${selectedCategory === category
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                    }`}
                            >
                                {category}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Products Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredProducts.map(product => (
                        <ProductCard
                            key={product.id}
                            product={product}
                            onAddToCart={() => addToCart(product)}
                        />
                    ))}
                </div>

                {filteredProducts.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-gray-400 text-xl">No products found</p>
                    </div>
                )}

                {/* Features Section */}
                <div className="mt-16 py-12 border-t border-gray-800">
                    <h2 className="text-3xl font-bold text-center mb-12 text-white">
                        Why Choose Quantum-Secure Commerce?
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 text-white">Post-Quantum Security</h3>
                            <p className="text-gray-400">
                                All transactions protected with CRYSTALS-Dilithium signatures, resistant to quantum attacks
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 text-white">Identity-Based Encryption</h3>
                            <p className="text-gray-400">
                                Your payment data encrypted with IBE, no complex key management needed
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 text-white">Lightning Fast</h3>
                            <p className="text-gray-400">
                                Optimized algorithms ensure security without sacrificing performance
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}