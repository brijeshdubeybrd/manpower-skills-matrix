import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Check for stored token on mount
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedEmail = localStorage.getItem('userEmail');
        if (storedToken) {
            // In a real app, verify token validity. Here we just assume it's valid for demo.
            setUser({ email: storedEmail || 'demo@example.com', role: 'admin' });
        }
    }, []);

    const login = async (email, password) => {
        setLoading(true);
        setError(null);
        try {
            await axios.post('/api/login', { email, password });
            // Simulate "OTP Sent" scenario - for this demo we'll assume OTP is always 123456
            return true;
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed');
            return false;
        } finally {
            setLoading(false);
        }
    };

    const verifyOtp = async (email, otp) => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('/api/verify-otp', { email, otp });
            const { access_token } = response.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('userEmail', email);
            setUser({ email, role: 'user' }); // Default role
            return true;
        } catch (err) {
            setError(err.response?.data?.detail || 'OTP verification failed');
            return false;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userEmail');
        setUser(null);
    };

    const value = {
        user,
        login,
        verifyOtp,
        logout,
        loading,
        error,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
