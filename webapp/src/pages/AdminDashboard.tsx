import { useState, useEffect } from 'react';
import axios from 'axios';
import {useAuth} from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Transaction {
    transaction_id: string;
    amount: number;
    currency: string;
    status: string;
    timestamp: string;
    customer_id: string;
}

interface Stats {
    total_transactions: number;
    total_revenue: number;
    active_users: number;
    success_rate: number;
}

export default function AdminDashboard() {
    const { token } = useAuth(); // Lấy token từ context thay vì props
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            // Fetch transactions
            const txResponse = await axios.get(`${API_URL}/api/admin/transactions`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTransactions(txResponse.data.transactions);

            // Fetch stats
            const statsResponse = await axios.get(`${API_URL}/api/admin/stats`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStats(statsResponse.data);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                    <h3 className="text-sm font-medium text-gray-400">Total Transactions</h3>
                    <p className="text-3xl font-bold text-primary mt-2">
                        {stats?.total_transactions || 0}
                    </p>
                </div>
                <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                    <h3 className="text-sm font-medium text-gray-400">Total Revenue</h3>
                    <p className="text-3xl font-bold text-green-400 mt-2">
                        ${stats?.total_revenue?.toFixed(2) || '0.00'}
                    </p>
                </div>
                <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                    <h3 className="text-sm font-medium text-gray-400">Active Users</h3>
                    <p className="text-3xl font-bold text-blue-400 mt-2">
                        {stats?.active_users || 0}
                    </p>
                </div>
                <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                    <h3 className="text-sm font-medium text-gray-400">Success Rate</h3>
                    <p className="text-3xl font-bold text-yellow-400 mt-2">
                        {stats?.success_rate?.toFixed(1) || '0'}%
                    </p>
                </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                <h2 className="text-xl font-bold mb-4">Recent Transactions</h2>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/10">
                                <th className="text-left py-3 px-4">Transaction ID</th>
                                <th className="text-left py-3 px-4">Amount</th>
                                <th className="text-left py-3 px-4">Status</th>
                                <th className="text-left py-3 px-4">Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transactions.map((tx) => (
                                <tr key={tx.transaction_id} className="border-b border-white/5">
                                    <td className="py-3 px-4 font-mono text-sm">
                                        {tx.transaction_id.substring(0, 8)}...
                                    </td>
                                    <td className="py-3 px-4">
                                        ${tx.amount} {tx.currency}
                                    </td>
                                    <td className="py-3 px-4">
                                        <span className={`px-2 py-1 rounded text-xs ${tx.status === 'completed'
                                                ? 'bg-green-500/20 text-green-400'
                                                : 'bg-red-500/20 text-red-400'
                                            }`}>
                                            {tx.status}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-sm text-gray-400">
                                        {new Date(tx.timestamp).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Crypto Keys Status */}
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                <h2 className="text-xl font-bold mb-4">Cryptographic Systems Status</h2>
                <div className="space-y-3">
                    <div className="flex justify-between items-center">
                        <span>IBE System</span>
                        <span className="text-green-400">✓ Active</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span>Dilithium Signatures</span>
                        <span className="text-green-400">✓ Active</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span>Key Rotation</span>
                        <span className="text-yellow-400">Next: 30 days</span>
                    </div>
                </div>
            </div>
        </div>
    );
}