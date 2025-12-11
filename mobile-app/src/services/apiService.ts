import axios, { AxiosResponse } from 'axios';
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change this to your backend URL
const API_TIMEOUT = 30000;

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    async (config) => {
        try {
            const token = await SecureStore.getItemAsync('authToken');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        } catch (error) {
            console.error('Error getting auth token:', error);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired, logout user
            await SecureStore.deleteItemAsync('authToken');
            await AsyncStorage.removeItem('userData');
            // You might want to navigate to login screen here
        }
        return Promise.reject(error);
    }
);

interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

export const apiService = {
    // Authentication
    async login(email: string, password: string): Promise<ApiResponse> {
        try {
            // FastAPI OAuth2PasswordRequestForm expects form data
            const formData = new FormData();
            formData.append('username', email); // OAuth2 uses 'username' field
            formData.append('password', password);

            const response: AxiosResponse = await api.post('/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Đăng nhập thất bại',
            };
        }
    },

    async register(userData: any): Promise<ApiResponse> {
        try {
            const response: AxiosResponse = await api.post('/auth/register', userData);
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Đăng ký thất bại',
            };
        }
    },

    async updateProfile(userData: any): Promise<ApiResponse> {
        try {
            const response: AxiosResponse = await api.put('/auth/me', userData);
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Cập nhật hồ sơ thất bại',
            };
        }
    },

    // Health Profile
    async getHealthProfile(): Promise<ApiResponse> {
        try {
            const response: AxiosResponse = await api.get('/auth/health-profile');
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Lấy thông tin sức khỏe thất bại',
            };
        }
    },

    async updateHealthMetrics(metrics: any): Promise<ApiResponse> {
        try {
            const response: AxiosResponse = await api.post('/auth/health-profile', metrics);
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Cập nhật chỉ số sức khỏe thất bại',
            };
        }
    },

    async updateMedicalHistory(history: any): Promise<ApiResponse> {
        try {
            // Update through health profile endpoint
            const response: AxiosResponse = await api.post('/auth/health-profile', history);
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Cập nhật tiền sử bệnh thất bại',
            };
        }
    },

    async updateNutritionGoals(goals: any): Promise<ApiResponse> {
        try {
            // Update through health profile endpoint
            const response: AxiosResponse = await api.post('/auth/health-profile', goals);
            return {
                success: true,
                data: response.data,
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Cập nhật mục tiêu dinh dưỡng thất bại',
            };
        }
    },

    // Food Analysis using new backend
    async analyzeFood(imageUri: string, foodName?: string): Promise<ApiResponse> {
        try {
            // If food name is provided, get nutrition info directly
            if (foodName) {
                const response: AxiosResponse = await api.get(`/test/foods`);

                if (response.data.status === 'success') {
                    // Find the food in the response
                    const allFoods = [
                        ...response.data.protein_foods,
                        response.data.rice_nutrition
                    ].filter(Boolean);

                    const food = allFoods.find(f =>
                        f.name.toLowerCase().includes(foodName.toLowerCase()) ||
                        foodName.toLowerCase().includes(f.name.toLowerCase())
                    );

                    if (food) {
                        return {
                            success: true,
                            data: {
                                foodName: food.name,
                                confidence: 0.95,
                                calories: food.calories || 0,
                                protein: food.protein || 0,
                                carbs: food.carbs || 0,
                                fat: food.fat || 0,
                                fiber: 0,
                                category: food.category,
                                healthAdvice: `${food.name} thuộc nhóm ${food.category}, cung cấp ${food.calories} calo/100g.`
                            },
                        };
                    }
                }
            }

            // Mock food detection from image for now
            const mockFoods = ['cơm trắng', 'thịt heo', 'cá hồi', 'rau muống', 'chuối'];
            const randomFood = mockFoods[Math.floor(Math.random() * mockFoods.length)];

            // Get nutrition info for the detected food
            const nutritionResponse = await this.analyzeFood('', randomFood);

            return nutritionResponse;
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Phân tích món ăn thất bại',
            };
        }
    },

    // Get health advice using new health advisor
    async getHealthAdvice(disease: string, foodName?: string): Promise<ApiResponse> {
        try {
            const requestData: any = { disease };
            if (foodName) {
                requestData.food_name = foodName;
            }

            const response: AxiosResponse = await api.post('/test/health-advice', requestData);

            if (response.data.status === 'success') {
                return {
                    success: true,
                    data: response.data.advice,
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Lấy lời khuyên sức khỏe thất bại',
                };
            }
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Lấy lời khuyên sức khỏe thất bại',
            };
        }
    },

    // Chat with Health Advisor
    async sendChatMessage(message: string, context?: any): Promise<ApiResponse> {
        try {
            // Parse message to detect health-related queries
            const lowerMessage = message.toLowerCase();

            // Check if it's a health advice query
            const diseases = ['tiểu đường', 'béo phì', 'huyết áp cao', 'diabetes', 'obesity', 'hypertension'];
            const detectedDisease = diseases.find(disease => lowerMessage.includes(disease));

            if (detectedDisease) {
                // Extract food name if mentioned
                const foods = ['cơm', 'thịt', 'cá', 'rau', 'trứng', 'bánh', 'phở'];
                const detectedFood = foods.find(food => lowerMessage.includes(food));

                const healthResponse = await this.getHealthAdvice(detectedDisease, detectedFood);

                if (healthResponse.success) {
                    const advice = healthResponse.data;
                    let responseText = `Tư vấn cho ${advice.bệnh || detectedDisease}:\n\n`;

                    if (advice.thông_tin_món_ăn) {
                        // Food-specific advice
                        responseText += `🍽️ Món ăn: ${advice.thông_tin_món_ăn.tên}\n`;
                        responseText += `📊 Mức độ an toàn: ${advice.mức_độ_an_toàn}\n`;
                        responseText += `⭐ Điểm số: ${advice.điểm_số}/100\n\n`;

                        if (advice.lời_khuyên_cụ_thể?.length > 0) {
                            responseText += `💡 Lời khuyên:\n${advice.lời_khuyên_cụ_thể.join('\n')}\n\n`;
                        }

                        if (advice.cách_điều_chỉnh?.length > 0) {
                            responseText += `🔧 Cách điều chỉnh:\n${advice.cách_điều_chỉnh.join('\n')}`;
                        }
                    } else {
                        // General advice
                        responseText += `⚠️ Cảnh báo: ${advice.cảnh_báo_nặng_nhất?.slice(0, 3).join(', ')}\n\n`;
                        responseText += `💡 ${advice.lời_khuyên_ngắn_gọn}\n\n`;
                        responseText += `🚫 Hạn chế: ${advice.hạn_chế_nghiêm_ngặt?.slice(0, 3).join(', ')}\n`;
                        responseText += `✅ Nên ăn: ${advice.nên_ăn_nhiều?.slice(0, 3).join(', ')}\n`;
                        responseText += `🍽️ Calo tối đa/bữa: ${advice.calo_tối_đa_mỗi_bữa} kcal`;
                    }

                    return {
                        success: true,
                        data: {
                            message: responseText,
                            type: 'health_advice',
                            timestamp: new Date().toISOString()
                        },
                    };
                }
            }

            // Default response for non-health queries
            return {
                success: true,
                data: {
                    message: "Xin chào! Tôi là trợ lý tư vấn dinh dưỡng. Bạn có thể hỏi tôi về:\n\n• Lời khuyên cho tiểu đường, béo phì, huyết áp cao\n• Phân tích món ăn cụ thể\n• Gợi ý thực phẩm phù hợp\n\nVí dụ: 'Tôi bị tiểu đường, ăn cơm trắng có được không?'",
                    type: 'general',
                    timestamp: new Date().toISOString()
                },
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Gửi tin nhắn thất bại',
            };
        }
    },

    // Recipe Generation
    async generateRecipe(ingredients: string[], preferences?: any): Promise<ApiResponse> {
        try {
            const requestData = {
                ingredients: ingredients.join(', '),
                dietary_restrictions: preferences?.dietaryRestrictions || [],
                health_conditions: preferences?.medicalConditions || [],
                allergies: preferences?.allergies || [],
                cuisine_preference: "vietnamese",
                meal_type: "any"
            };

            const response: AxiosResponse = await api.post('/recipes/suggest', requestData);

            // Transform response to match mobile app expectations
            const recipeData = response.data;
            return {
                success: true,
                data: {
                    id: recipeData.query_id || Date.now().toString(),
                    name: recipeData.recipe_name || "Công thức từ nguyên liệu",
                    ingredients: ingredients,
                    instructions: recipeData.instructions || [],
                    cookingTime: recipeData.cooking_time || 30,
                    servings: recipeData.servings || 2,
                    difficulty: recipeData.difficulty || "Trung bình",
                    nutrition: {
                        calories: recipeData.nutrition?.calories || 400,
                        protein: recipeData.nutrition?.protein || 20,
                        carbs: recipeData.nutrition?.carbs || 50,
                        fat: recipeData.nutrition?.fat || 15,
                    },
                    healthBenefits: recipeData.health_benefits || [],
                    warnings: recipeData.warnings || []
                },
            };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Tạo công thức thất bại',
            };
        }
    },

    async analyzeIngredients(imageUri: string): Promise<ApiResponse> {
        try {
            // Mock ingredient detection for now
            // In a real implementation, you'd need an image analysis service
            const mockIngredients = [
                "Thịt bò",
                "Hành tây",
                "Cà chua",
                "Rau thơm"
            ];

            return {
                success: true,
                data: {
                    ingredients: mockIngredients
                },
            };
        } catch (error: any) {
            return {
                success: false,
                error: 'Phân tích nguyên liệu thất bại',
            };
        }
    },

    // Nutrition Tracking
    async getDailyNutrition(date: string): Promise<ApiResponse> {
        try {
            // Mock daily nutrition data for now
            // In a real implementation, this would come from meals history
            const mockData = {
                totalCalories: 1850,
                protein: 85,
                carbs: 220,
                fat: 65,
                fiber: 28,
                meals: [
                    { name: "Phở bò", calories: 450, time: "07:30" },
                    { name: "Cơm trưa", calories: 650, time: "12:00" },
                    { name: "Cơm tối", calories: 550, time: "18:30" },
                    { name: "Snack", calories: 200, time: "15:00" }
                ]
            };

            return {
                success: true,
                data: mockData,
            };
        } catch (error: any) {
            return {
                success: false,
                error: 'Lấy thông tin dinh dưỡng thất bại',
            };
        }
    },

    async addFoodEntry(foodData: any): Promise<ApiResponse> {
        try {
            // Mock adding food entry
            // In a real implementation, this would save to meals history
            return {
                success: true,
                data: {
                    id: Date.now().toString(),
                    ...foodData,
                    timestamp: new Date().toISOString()
                },
            };
        } catch (error: any) {
            return {
                success: false,
                error: 'Thêm món ăn thất bại',
            };
        }
    },

    // Notifications - Mock for now
    async getNotifications(): Promise<ApiResponse> {
        try {
            // Mock notifications - in real app these would come from backend
            return {
                success: true,
                data: [], // Will be handled by NotificationScreen with mock data
            };
        } catch (error: any) {
            return {
                success: false,
                error: 'Lấy thông báo thất bại',
            };
        }
    },

    async markNotificationRead(notificationId: string): Promise<ApiResponse> {
        try {
            // Mock marking as read
            return {
                success: true,
                data: { id: notificationId, read: true },
            };
        } catch (error: any) {
            return {
                success: false,
                error: 'Đánh dấu đã đọc thất bại',
            };
        }
    },
};