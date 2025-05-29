import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface User {
  email: string;
  user_id: string;
}

interface PaymentStatus {
  success: boolean;
  payment_id?: string;
  transaction_id?: string;
  signature?: string;
  timestamp?: string;
  status?: string;
  message?: string;
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<User | null>(null);
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });

  const [paymentForm, setPaymentForm] = useState({
    amount: '',
    cardNumber: '',
    expMonth: '',
    expYear: '',
    cvv: ''
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email: loginForm.email,
        password: loginForm.password
      });

      const data = response.data;
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setUser({
        email: data.email,
        user_id: data.user_id
      });
    } catch (error: any) {
      alert(`Login failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setPaymentStatus(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/payments/process`,
        {
          amount: parseFloat(paymentForm.amount),
          currency: 'USD',
          payment_method: 'credit_card',
          card_data: {
            number: paymentForm.cardNumber.replace(/\s/g, ''),
            exp_month: paymentForm.expMonth,
            exp_year: paymentForm.expYear,
            cvv: paymentForm.cvv
          },
          billing_address: {
            name: user?.email || 'Customer',
            street: '123 Main St',
            city: 'Anytown',
            state: 'CA',
            zip: '12345'
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setPaymentStatus({
        success: true,
        ...response.data
      });
    } catch (error: any) {
      setPaymentStatus({
        success: false,
        message: error.response?.data?.detail || 'Payment failed'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setPaymentStatus(null);
  };

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

  return (
    <div className="min-h-screen bg-dark text-white">
      {/* Header */}
      <header className="bg-gradient-to-r from-secondary to-blue-600 p-8 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-4xl font-bold flex items-center gap-2">
            🔐 Quantum-Secure E-Commerce
          </h1>
          <p className="text-lg mt-2 opacity-90">Post-Quantum Secure Payment System</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-8 max-w-4xl">
        {!token ? (
          /* Login Form */
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-8 shadow-2xl border border-white/10">
            <h2 className="text-3xl font-bold text-primary mb-6">Login</h2>
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">
                  Email:
                </label>
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  required
                  placeholder="user@example.com"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">
                  Password:
                </label>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  required
                  placeholder="Enter password"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-primary to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg hover:scale-[1.02] transition-all disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? 'Logging in...' : 'Login'}
              </button>
            </form>
            <p className="mt-4 text-sm text-gray-400 italic text-center">
              Demo credentials: Any valid email format
            </p>
          </div>
        ) : (
          /* Payment Form */
          <div className="space-y-6">
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 shadow-xl border border-white/10">
              <div className="flex justify-between items-center">
                <p>Logged in as: <span className="font-bold text-primary">{user?.email}</span></p>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all"
                >
                  Logout
                </button>
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-8 shadow-2xl border border-white/10">
              <h2 className="text-3xl font-bold text-primary mb-6">Make a Payment</h2>
              <form onSubmit={handlePayment} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-300">
                    Amount (USD):
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={paymentForm.amount}
                    onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
                    required
                    placeholder="99.99"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-300">
                    Card Number:
                  </label>
                  <input
                    type="text"
                    value={paymentForm.cardNumber}
                    onChange={(e) => setPaymentForm({
                      ...paymentForm,
                      cardNumber: formatCardNumber(e.target.value)
                    })}
                    maxLength={19}
                    required
                    placeholder="4111 1111 1111 1111"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      Exp Month:
                    </label>
                    <input
                      type="text"
                      value={paymentForm.expMonth}
                      onChange={(e) => setPaymentForm({ ...paymentForm, expMonth: e.target.value })}
                      maxLength={2}
                      required
                      placeholder="12"
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      Exp Year:
                    </label>
                    <input
                      type="text"
                      value={paymentForm.expYear}
                      onChange={(e) => setPaymentForm({ ...paymentForm, expYear: e.target.value })}
                      maxLength={4}
                      required
                      placeholder="2025"
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      CVV:
                    </label>
                    <input
                      type="text"
                      value={paymentForm.cvv}
                      onChange={(e) => setPaymentForm({ ...paymentForm, cvv: e.target.value })}
                      maxLength={3}
                      required
                      placeholder="123"
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-primary to-blue-600 text-white font-bold py-4 px-6 rounded-lg hover:shadow-lg hover:scale-[1.02] transition-all disabled:opacity-60 disabled:cursor-not-allowed text-lg"
                >
                  {loading ? 'Processing...' : '💳 Pay Securely'}
                </button>
              </form>

              {paymentStatus && (
                <div className={`mt-6 p-6 rounded-lg ${paymentStatus.success
                    ? 'bg-green-500/10 border border-green-500/30'
                    : 'bg-red-500/10 border border-red-500/30'
                  }`}>
                  <h3 className="text-xl font-bold mb-4">
                    {paymentStatus.success ? '✅ Payment Successful!' : '❌ Payment Failed'}
                  </h3>
                  {paymentStatus.success ? (
                    <div className="space-y-2">
                      <p><span className="font-semibold">Payment ID:</span> {paymentStatus.payment_id}</p>
                      <p><span className="font-semibold">Transaction ID:</span> {paymentStatus.transaction_id}</p>
                      <p><span className="font-semibold">Status:</span> {paymentStatus.status}</p>
                      <p><span className="font-semibold">Timestamp:</span> {new Date(paymentStatus.timestamp!).toLocaleString()}</p>
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <p className="font-semibold mb-2">Digital Signature (Dilithium):</p>
                        <code className="block bg-black/30 p-3 rounded text-xs break-all">
                          {paymentStatus.signature?.substring(0, 64)}...
                        </code>
                      </div>
                    </div>
                  ) : (
                    <p>{paymentStatus.message}</p>
                  )}
                </div>
              )}
            </div>

            <div className="bg-primary/5 backdrop-blur-lg rounded-xl p-6 shadow-xl border border-primary/20">
              <h3 className="text-xl font-bold text-primary mb-4">🔒 Security Features</h3>
              <ul className="space-y-2 text-gray-300">
                <li>✓ Identity-Based Encryption (IBE) for payment data</li>
                <li>✓ Post-Quantum Digital Signatures (CRYSTALS-Dilithium)</li>
                <li>✓ End-to-end encryption</li>
                <li>✓ Quantum-resistant cryptography</li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 p-8 bg-black/30 text-center text-gray-400">
        <p>© 2024 Quantum-Secure Commerce. Protected by post-quantum cryptography.</p>
      </footer>
    </div>
  );
}

export default App;