import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';

// Mock products data - should match HomePage
const MOCK_PRODUCTS = [
    {
        id: '1',
        name: 'Quantum-Safe Laptop',
        description: 'Laptop với mã hóa quantum-resistant built-in',
        longDescription: 'Experience unparalleled security with our quantum-safe laptop. Features military-grade encryption, secure boot process, and hardware-based security modules designed to withstand quantum computing attacks.',
        price: 1299.99,
        image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
        category: 'Electronics',
        features: ['Post-Quantum Encryption', 'Secure Boot', 'Hardware Security Module', '16GB RAM', '512GB SSD', 'Intel Core i7'],
        inStock: true,
        specs: {
            'Processor': 'Intel Core i7-12700H',
            'Memory': '16GB DDR5',
            'Storage': '512GB NVMe SSD',
            'Display': '15.6" FHD IPS',
            'Security': 'TPM 2.0 + Quantum Module',
            'OS': 'Windows 11 Pro'
        }
    },
    {
        id: '2',
        name: 'Crypto Hardware Wallet',
        description: 'Hardware wallet với Dilithium signatures',
        longDescription: 'The most secure hardware wallet on the market, featuring post-quantum cryptographic signatures using CRYSTALS-Dilithium. Protect your digital assets against future quantum threats.',
        price: 199.99,
        image: 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=500',
        category: 'Security',
        features: ['CRYSTALS-Dilithium', 'Quantum-Safe', 'USB-C', 'OLED Display', 'Open Source Firmware'],
        inStock: true,
        specs: {
            'Algorithms': 'Dilithium2, Dilithium3',
            'Display': '128x64 OLED',
            'Connectivity': 'USB-C',
            'Battery': '100mAh',
            'Compatibility': 'Windows/Mac/Linux',
            'Certifications': 'CC EAL5+'
        }
    },
    // Add other products...
];

export default function ProductDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { addToCart } = useCart();
    const [quantity, setQuantity] = useState(1);
    const [selectedImage, setSelectedImage] = useState(0);

    const product = MOCK_PRODUCTS.find(p => p.id === id);

    if (!product) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-white mb-4">Product Not Found</h1>
                    <button
                        onClick={() => navigate('/')}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                    >
                        Back to Products
                    </button>
                </div>
            </div>
        );
    }

    const handleAddToCart = () => {
        for (let i = 0; i < quantity; i++) {
            addToCart(product);
        }
        navigate('/cart');
    };

    return (
        <div className="min-h-screen bg-gray-900 py-12">
            <div className="container mx-auto px-4">
                {/* Breadcrumb */}
                <nav className="text-gray-400 mb-8">
                    <ol className="flex items-center space-x-2">
                        <li><a href="/" className="hover:text-white">Home</a></li>
                        <li>/</li>
                        <li><a href="/" className="hover:text-white">Products</a></li>
                        <li>/</li>
                        <li className="text-white">{product.name}</li>
                    </ol>
                </nav>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Product Images */}
                    <div>
                        <div className="bg-gray-800 rounded-lg overflow-hidden mb-4">
                            <img
                                src={product.image}
                                alt={product.name}
                                className="w-full h-96 object-cover"
                            />
                        </div>

                        {/* Thumbnail gallery (mock) */}
                        <div className="grid grid-cols-4 gap-2">
                            {[1, 2, 3, 4].map((i) => (
                                <button
                                    key={i}
                                    className={`bg-gray-800 rounded-lg overflow-hidden ${selectedImage === i - 1 ? 'ring-2 ring-blue-500' : ''
                                        }`}
                                    onClick={() => setSelectedImage(i - 1)}
                                >
                                    <img
                                        src={product.image}
                                        alt={`${product.name} ${i}`}
                                        className="w-full h-20 object-cover opacity-70 hover:opacity-100"
                                    />
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Product Info */}
                    <div>
                        <div className="mb-6">
                            <span className="text-sm text-gray-400 bg-gray-800 px-3 py-1 rounded-full">
                                {product.category}
                            </span>
                            <h1 className="text-3xl font-bold text-white mt-4 mb-2">{product.name}</h1>
                            <p className="text-gray-400">{product.longDescription}</p>
                        </div>

                        {/* Price and Stock */}
                        <div className="mb-6">
                            <div className="flex items-baseline gap-4">
                                <span className="text-4xl font-bold text-white">${product.price}</span>
                                {product.inStock ? (
                                    <span className="text-green-400 flex items-center gap-1">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                        In Stock
                                    </span>
                                ) : (
                                    <span className="text-red-400">Out of Stock</span>
                                )}
                            </div>
                        </div>

                        {/* Features */}
                        <div className="mb-6">
                            <h3 className="text-white font-semibold mb-3">Key Features</h3>
                            <div className="flex flex-wrap gap-2">
                                {product.features.map((feature, index) => (
                                    <span
                                        key={index}
                                        className="bg-blue-600/20 text-blue-400 px-3 py-1 rounded-full text-sm"
                                    >
                                        {feature}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Quantity and Add to Cart */}
                        <div className="flex items-center gap-4 mb-8">
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                    className="w-10 h-10 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center justify-center"
                                >
                                    -
                                </button>
                                <input
                                    type="number"
                                    value={quantity}
                                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                                    className="w-16 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-center"
                                />
                                <button
                                    onClick={() => setQuantity(quantity + 1)}
                                    className="w-10 h-10 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center justify-center"
                                >
                                    +
                                </button>
                            </div>

                            <button
                                onClick={handleAddToCart}
                                disabled={!product.inStock}
                                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Add to Cart
                            </button>
                        </div>

                        {/* Security Badge */}
                        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 mb-8">
                            <div className="flex items-center gap-3">
                                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                                <div>
                                    <p className="text-green-400 font-semibold">Quantum-Safe Purchase</p>
                                    <p className="text-green-300 text-sm">
                                        This transaction will be protected by post-quantum cryptography
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Specifications */}
                        {product.specs && (
                            <div>
                                <h3 className="text-white font-semibold mb-3">Specifications</h3>
                                <div className="bg-gray-800 rounded-lg p-4">
                                    <dl className="space-y-2">
                                        {Object.entries(product.specs).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <dt className="text-gray-400">{key}:</dt>
                                                <dd className="text-white">{value}</dd>
                                            </div>
                                        ))}
                                    </dl>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}