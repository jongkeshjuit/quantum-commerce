
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface PrivateRouteProps {
    requiredRole?: string;
}

export default function PrivateRoute({ requiredRole }: PrivateRouteProps) {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        // Loading spinner
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (!user) {
        // Redirect to login with return URL
        return <Navigate to={`/login?redirect=${location.pathname}`} state={{ from: location }} replace />;
    }

    if (requiredRole && user.user_type !== requiredRole) {
        // User doesn't have required role
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">🚫</div>
                    <h1 className="text-2xl font-bold text-white mb-2">Access Denied</h1>
                    <p className="text-gray-400">You don't have permission to access this page.</p>
                </div>
            </div>
        );
    }

    return <Outlet />;
}