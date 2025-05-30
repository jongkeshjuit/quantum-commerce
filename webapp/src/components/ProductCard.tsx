
import { Link } from 'react-router-dom';

interface Product {
    id: string;
    name: string;
    description: string;
    price: number;
    image: string;
    category: string;
    features?: string[];
}

interface ProductCardProps {
    product: Product;
    onAddToCart: () => void;
}

export default function ProductCard({ product, onAddToCart }: ProductCardProps) {
    return (
        <div className="bg-gray-800 rounded-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
            <Link to={`/product/${product.id}`}>
                <div className="aspect-w-16 aspect-h-9 overflow-hidden">
                    <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-48 object-cover hover:scale-105 transition-transform duration-300"
                    />
                </div>
            </Link>

            <div className="p-6">
                <div className="flex items-start justify-between mb-2">
                    <h3 className="text-xl font-semibold text-white">{product.name}</h3>
                    <span className="text-sm text-gray-400 bg-gray-700 px-2 py-1 rounded">
                        {product.category}
                    </span>
                </div>

                <p className="text-gray-400 text-sm mb-4">{product.description}</p>

                {product.features && (
                    <div className="mb-4">
                        <div className="flex flex-wrap gap-2">
                            {product.features.slice(0, 2).map((feature, index) => (
                                <span
                                    key={index}
                                    className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded"
                                >
                                    {feature}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-white">${product.price}</span>

                    <div className="flex gap-2">
                        <Link
                            to={`/product/${product.id}`}
                            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        >
                            Details
                        </Link>
                        <button
                            onClick={onAddToCart}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                            </svg>
                            Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}