import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { apiService } from '../src/services/apiService';

interface User {
    id: string;
    email: string;
    name: string;
    avatar?: string;
    medicalConditions?: string[];
    allergies?: string[];
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    register: (userData: RegisterData) => Promise<boolean>;
    logout: () => Promise<void>;
    updateProfile: (userData: Partial<User>) => Promise<boolean>;
}

interface RegisterData {
    name: string;
    email: string;
    password: string;
    phone?: string;
    dateOfBirth?: string;
    gender?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const token = await SecureStore.getItemAsync('authToken');
            const userData = await AsyncStorage.getItem('userData');

            if (token && userData) {
                const parsedUser = JSON.parse(userData);
                setUser(parsedUser);
            }
        } catch (error) {
            console.error('Auth check error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (email: string, password: string): Promise<boolean> => {
        try {
            setIsLoading(true);
            const response = await apiService.login(email, password);

            if (response.success && response.data) {
                const { token, user: userData } = response.data;

                await SecureStore.setItemAsync('authToken', token);
                await AsyncStorage.setItem('userData', JSON.stringify(userData));

                setUser(userData);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (userData: RegisterData): Promise<boolean> => {
        try {
            setIsLoading(true);
            const response = await apiService.register(userData);

            if (response.success && response.data) {
                const { token, user: newUser } = response.data;

                await SecureStore.setItemAsync('authToken', token);
                await AsyncStorage.setItem('userData', JSON.stringify(newUser));

                setUser(newUser);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Register error:', error);
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = async (): Promise<void> => {
        try {
            await SecureStore.deleteItemAsync('authToken');
            await AsyncStorage.removeItem('userData');
            setUser(null);
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const updateProfile = async (userData: Partial<User>): Promise<boolean> => {
        try {
            const response = await apiService.updateProfile(userData);

            if (response.success && response.data) {
                const updatedUser = { ...user, ...response.data };
                await AsyncStorage.setItem('userData', JSON.stringify(updatedUser));
                setUser(updatedUser);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Update profile error:', error);
            return false;
        }
    };

    const value: AuthContextType = {
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};