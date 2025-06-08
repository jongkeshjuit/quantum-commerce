import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Transaction {
    transaction_id: string;
    amount: number;
    currency: string;
    status: string;
    timestamp: string;
}

export default function OrderHistoryPage() {
    const { token } = useAuth();
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTransaction, setSelectedTransaction] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchTransactions();
    }, []);

    const fetchTransactions = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/transactions`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTransactions(response.data.transactions);
        } catch (error) {
            console.error('Failed to fetch transactions:', error);
        } finally {
            setLoading(false);
        }
    };

    const verifyTransaction = async (transactionId: string) => {
        try {
            const response = await axios.post(
                `${API_URL}/api/payments/verify`,
                { transaction_id: transactionId },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            if (response.data.verified) {
                alert('✅ Transaction signature verified successfully!');
            } else {
                alert('❌ Transaction signature verification failed');
            }
        } catch (error) {
            console.error('Verification failed:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 py-12">
            <div className="container mx-auto px-4">
                <h1 className="text-3xl font-bold text-white mb-8">Order History</h1>

                {transactions.length === 0 ? (
                    <div className="bg-gray-800 rounded-lg p-12 text-center">
                        <svg className="w-24 h-24 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <h2 className="text-xl font-semibold text-white mb-2">No Orders Yet</h2>
                        <p className="text-gray-400 mb-6">
                            Start shopping to see your quantum-secured transactions here!
                        </p>
                        <Link
                            to="/"
                            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Start Shopping
                        </Link>
                    </div>
                ) : (
                    <div className="bg-gray-800 rounded-lg overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-700">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                        Order ID
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                        Date
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                        Amount
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                        Security
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {transactions.map((transaction) => (
                                    <tr key={transaction.transaction_id} className="hover:bg-gray-700/50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="text-white font-mono text-sm">
                                                {transaction.transaction_id}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-gray-300">
                                            {new Date(transaction.timestamp).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-white">
                                            ${transaction.amount.toFixed(2)} {transaction.currency}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${transaction.status === 'completed'
                                                    ? 'bg-green-900/20 text-green-400 border border-green-500/30'
                                                    : 'bg-yellow-900/20 text-yellow-400 border border-yellow-500/30'
                                                }`}>
                                                {transaction.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center gap-2">
                                                <span className="text-green-400" title="IBE Encrypted">
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                                    </svg>
                                                </span>
                                                <span className="text-blue-400" title="Dilithium Signed">
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                                    </svg>
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            <button
                                                onClick={() => verifyTransaction(transaction.transaction_id)}
                                                className="text-blue-400 hover:text-blue-300 mr-3"
                                            >
                                                Verify
                                            </button>
                                            <button
                                                onClick={() => navigate(`/order-details/${transaction.transaction_id}`)}
                                                className="text-gray-400 hover:text-white"
                                            >
                                                Details
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Security Info */}
                <div className="mt-8 bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
                    <h3 className="text-blue-400 font-semibold mb-3">About Your Transaction Security</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div className="flex items-start gap-3">
                            <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                            <div>
                                <p className="text-blue-300 font-medium">IBE Encryption</p>
                                <p className="text-blue-200">
                                    All payment data encrypted with your identity-based key
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                            <div>
                                <p className="text-blue-300 font-medium">Dilithium Signatures</p>
                                <p className="text-blue-200">
                                    Every transaction signed with quantum-resistant signatures
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}