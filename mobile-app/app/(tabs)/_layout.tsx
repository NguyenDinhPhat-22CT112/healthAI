import { Tabs } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';

const COLORS = {
    primary: '#2E7D32',
    gray: '#757575',
    white: '#FFFFFF',
    lightGray: '#E0E0E0',
};

export default function TabLayout() {
    return (
        <Tabs
            screenOptions={{
                tabBarActiveTintColor: COLORS.primary,
                tabBarInactiveTintColor: COLORS.gray,
                tabBarStyle: {
                    backgroundColor: COLORS.white,
                    borderTopColor: COLORS.lightGray,
                    height: 60,
                    paddingBottom: 8,
                    paddingTop: 8,
                },
                headerStyle: {
                    backgroundColor: COLORS.primary,
                },
                headerTintColor: COLORS.white,
                headerTitleStyle: {
                    fontWeight: 'bold',
                },
            }}
        >
            <Tabs.Screen
                name="index"
                options={{
                    title: 'Trang chủ',
                    tabBarIcon: ({ color, size }) => (
                        <MaterialIcons name="home" size={size} color={color} />
                    ),
                }}
            />
            <Tabs.Screen
                name="camera"
                options={{
                    title: 'Tính Calo',
                    tabBarIcon: ({ color, size }) => (
                        <MaterialIcons name="camera-alt" size={size} color={color} />
                    ),
                }}
            />
            <Tabs.Screen
                name="chat"
                options={{
                    title: 'Tư vấn',
                    tabBarIcon: ({ color, size }) => (
                        <MaterialIcons name="chat" size={size} color={color} />
                    ),
                }}
            />
            <Tabs.Screen
                name="recipe"
                options={{
                    title: 'Công thức',
                    tabBarIcon: ({ color, size }) => (
                        <MaterialIcons name="restaurant" size={size} color={color} />
                    ),
                }}
            />
            <Tabs.Screen
                name="profile"
                options={{
                    title: 'Hồ sơ',
                    tabBarIcon: ({ color, size }) => (
                        <MaterialIcons name="person" size={size} color={color} />
                    ),
                }}
            />
        </Tabs>
    );
}