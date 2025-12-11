import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../src/services/apiService';

interface HealthMetrics {
    weight: number;
    height: number;
    bmi: number;
    bloodPressure?: string;
    bloodSugar?: number;
    cholesterol?: number;
    lastUpdated: string;
}

interface MedicalHistory {
    conditions: string[];
    allergies: string[];
    medications: string[];
    dietaryRestrictions: string[];
}

interface NutritionGoals {
    dailyCalories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    sodium: number;
}

interface HealthContextType {
    healthMetrics: HealthMetrics | null;
    medicalHistory: MedicalHistory | null;
    nutritionGoals: NutritionGoals | null;
    isLoading: boolean;
    updateHealthMetrics: (metrics: Partial<HealthMetrics>) => Promise<boolean>;
    updateMedicalHistory: (history: Partial<MedicalHistory>) => Promise<boolean>;
    updateNutritionGoals: (goals: Partial<NutritionGoals>) => Promise<boolean>;
    getDailyNutritionSummary: (date: string) => Promise<any>;
    addFoodEntry: (foodData: any) => Promise<boolean>;
}

const HealthContext = createContext<HealthContextType | undefined>(undefined);

export const useHealth = () => {
    const context = useContext(HealthContext);
    if (!context) {
        throw new Error('useHealth must be used within a HealthProvider');
    }
    return context;
};

interface HealthProviderProps {
    children: ReactNode;
}

export const HealthProvider: React.FC<HealthProviderProps> = ({ children }) => {
    const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(null);
    const [medicalHistory, setMedicalHistory] = useState<MedicalHistory | null>(null);
    const [nutritionGoals, setNutritionGoals] = useState<NutritionGoals | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        loadHealthData();
    }, []);

    const loadHealthData = async () => {
        try {
            setIsLoading(true);

            // Load from local storage first
            const [metricsData, historyData, goalsData] = await Promise.all([
                AsyncStorage.getItem('healthMetrics'),
                AsyncStorage.getItem('medicalHistory'),
                AsyncStorage.getItem('nutritionGoals'),
            ]);

            if (metricsData) setHealthMetrics(JSON.parse(metricsData));
            if (historyData) setMedicalHistory(JSON.parse(historyData));
            if (goalsData) setNutritionGoals(JSON.parse(goalsData));

            // Sync with server
            const response = await apiService.getHealthProfile();
            if (response.success && response.data) {
                const { metrics, history, goals } = response.data;

                if (metrics) {
                    setHealthMetrics(metrics);
                    await AsyncStorage.setItem('healthMetrics', JSON.stringify(metrics));
                }

                if (history) {
                    setMedicalHistory(history);
                    await AsyncStorage.setItem('medicalHistory', JSON.stringify(history));
                }

                if (goals) {
                    setNutritionGoals(goals);
                    await AsyncStorage.setItem('nutritionGoals', JSON.stringify(goals));
                }
            }
        } catch (error) {
            console.error('Load health data error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const updateHealthMetrics = async (metrics: Partial<HealthMetrics>): Promise<boolean> => {
        try {
            const updatedMetrics = {
                ...healthMetrics,
                ...metrics,
                lastUpdated: new Date().toISOString(),
            };

            // Calculate BMI if weight and height are provided
            if (updatedMetrics.weight && updatedMetrics.height) {
                const heightInMeters = updatedMetrics.height / 100;
                updatedMetrics.bmi = Number((updatedMetrics.weight / (heightInMeters * heightInMeters)).toFixed(1));
            }

            const response = await apiService.updateHealthMetrics(updatedMetrics);

            if (response.success) {
                setHealthMetrics(updatedMetrics);
                await AsyncStorage.setItem('healthMetrics', JSON.stringify(updatedMetrics));
                return true;
            }
            return false;
        } catch (error) {
            console.error('Update health metrics error:', error);
            return false;
        }
    };

    const updateMedicalHistory = async (history: Partial<MedicalHistory>): Promise<boolean> => {
        try {
            const updatedHistory = {
                ...medicalHistory,
                ...history,
            };

            const response = await apiService.updateMedicalHistory(updatedHistory);

            if (response.success) {
                setMedicalHistory(updatedHistory);
                await AsyncStorage.setItem('medicalHistory', JSON.stringify(updatedHistory));
                return true;
            }
            return false;
        } catch (error) {
            console.error('Update medical history error:', error);
            return false;
        }
    };

    const updateNutritionGoals = async (goals: Partial<NutritionGoals>): Promise<boolean> => {
        try {
            const updatedGoals = {
                ...nutritionGoals,
                ...goals,
            };

            const response = await apiService.updateNutritionGoals(updatedGoals);

            if (response.success) {
                setNutritionGoals(updatedGoals);
                await AsyncStorage.setItem('nutritionGoals', JSON.stringify(updatedGoals));
                return true;
            }
            return false;
        } catch (error) {
            console.error('Update nutrition goals error:', error);
            return false;
        }
    };

    const getDailyNutritionSummary = async (date: string) => {
        try {
            const response = await apiService.getDailyNutrition(date);
            return response.data || null;
        } catch (error) {
            console.error('Get daily nutrition error:', error);
            return null;
        }
    };

    const addFoodEntry = async (foodData: any): Promise<boolean> => {
        try {
            const response = await apiService.addFoodEntry(foodData);
            return response.success;
        } catch (error) {
            console.error('Add food entry error:', error);
            return false;
        }
    };

    const value: HealthContextType = {
        healthMetrics,
        medicalHistory,
        nutritionGoals,
        isLoading,
        updateHealthMetrics,
        updateMedicalHistory,
        updateNutritionGoals,
        getDailyNutritionSummary,
        addFoodEntry,
    };

    return (
        <HealthContext.Provider value={value}>
            {children}
        </HealthContext.Provider>
    );
};