import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import Toast from 'react-native-toast-message';
import { AuthProvider } from '../contexts/AuthContext';
import { HealthProvider } from '../contexts/HealthContext';

const COLORS = {
    primary: '#2E7D32',
    white: '#FFFFFF',
};

export default function RootLayout() {
    return (
        <GestureHandlerRootView style={{ flex: 1 }}>
            <SafeAreaProvider>
                <AuthProvider>
                    <HealthProvider>
                        <Stack
                            screenOptions={{
                                headerStyle: {
                                    backgroundColor: COLORS.primary,
                                },
                                headerTintColor: COLORS.white,
                                headerTitleStyle: {
                                    fontWeight: 'bold',
                                },
                            }}
                        >
                            <Stack.Screen
                                name="(tabs)"
                                options={{ headerShown: false }}
                            />
                            <Stack.Screen
                                name="auth/login"
                                options={{
                                    title: 'Đăng nhập',
                                    presentation: 'modal'
                                }}
                            />
                            <Stack.Screen
                                name="auth/register"
                                options={{
                                    title: 'Đăng ký',
                                    presentation: 'modal'
                                }}
                            />
                            <Stack.Screen
                                name="health/info"
                                options={{
                                    title: 'Thông tin sức khỏe',
                                    presentation: 'modal'
                                }}
                            />
                        </Stack>
                        <StatusBar style="light" backgroundColor={COLORS.primary} />
                        <Toast />
                    </HealthProvider>
                </AuthProvider>
            </SafeAreaProvider>
        </GestureHandlerRootView>
    );
}