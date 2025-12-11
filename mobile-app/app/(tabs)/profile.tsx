import React, { useState } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    Alert,
    Switch,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { useHealth } from '../../contexts/HealthContext';

const COLORS = {
    primary: '#2E7D32',
    primaryLight: '#4CAF50',
    primaryLighter: '#81C784',
    white: '#FFFFFF',
    gray: '#757575',
    lightGray: '#E0E0E0',
    textPrimary: '#212121',
    textSecondary: '#757575',
    success: '#4CAF50',
    warning: '#FF9800',
    error: '#F44336',
    background: '#F5F5F5',
};

export default function ProfileScreen() {
    const { user, logout } = useAuth();
    const { healthMetrics, medicalHistory } = useHealth();
    const [notificationsEnabled, setNotificationsEnabled] = useState(true);
    const [darkModeEnabled, setDarkModeEnabled] = useState(false);

    const handleLogout = () => {
        Alert.alert(
            'Đăng xuất',
            'Bạn có chắc chắn muốn đăng xuất?',
            [
                { text: 'Hủy', style: 'cancel' },
                {
                    text: 'Đăng xuất',
                    style: 'destructive',
                    onPress: logout
                },
            ]
        );
    };

    const menuItems = [
        {
            icon: 'person',
            title: 'Thông tin cá nhân',
            subtitle: 'Cập nhật thông tin tài khoản',
            onPress: () => {/* Navigate to personal info */ },
        },
        {
            icon: 'favorite',
            title: 'Thông tin sức khỏe',
            subtitle: 'Quản lý chỉ số và tiền sử bệnh',
            onPress: () => {/* Navigate to health info */ },
        },
        {
            icon: 'notifications',
            title: 'Thông báo',
            subtitle: 'Cài đặt nhắc nhở và thông báo',
            onPress: () => {/* Navigate to notifications */ },
        },
        {
            icon: 'history',
            title: 'Lịch sử ăn uống',
            subtitle: 'Xem lại các bữa ăn đã ghi nhận',
            onPress: () => {/* Navigate to history */ },
        },
        {
            icon: 'analytics',
            title: 'Báo cáo sức khỏe',
            subtitle: 'Thống kê và phân tích dinh dưỡng',
            onPress: () => {/* Navigate to reports */ },
        },
        {
            icon: 'help',
            title: 'Trợ giúp & Hỗ trợ',
            subtitle: 'FAQ và liên hệ hỗ trợ',
            onPress: () => {/* Navigate to help */ },
        },
        {
            icon: 'privacy-tip',
            title: 'Chính sách bảo mật',
            subtitle: 'Điều khoản sử dụng và bảo mật',
            onPress: () => {/* Navigate to privacy */ },
        },
    ];

    const getBMIStatus = (bmi: number) => {
        if (bmi < 18.5) return { status: 'Thiếu cân', color: COLORS.warning };
        if (bmi < 25) return { status: 'Bình thường', color: COLORS.success };
        if (bmi < 30) return { status: 'Thừa cân', color: COLORS.warning };
        return { status: 'Béo phì', color: COLORS.error };
    };

    return (
        <ScrollView style={styles.container}>
            {/* Profile Header */}
            <LinearGradient
                colors={[COLORS.primary, COLORS.primaryLight]}
                style={styles.header}
            >
                <View style={styles.profileInfo}>
                    <View style={styles.avatar}>
                        <MaterialIcons name="person" size={40} color={COLORS.white} />
                    </View>
                    <View style={styles.userInfo}>
                        <Text style={styles.userName}>{user?.name || 'Người dùng'}</Text>
                        <Text style={styles.userEmail}>{user?.email}</Text>
                    </View>
                    <TouchableOpacity style={styles.editButton}>
                        <MaterialIcons name="edit" size={20} color={COLORS.white} />
                    </TouchableOpacity>
                </View>
            </LinearGradient>

            {/* Health Summary */}
            {healthMetrics && (
                <View style={styles.healthSummary}>
                    <Text style={styles.sectionTitle}>Tổng quan sức khỏe</Text>
                    <View style={styles.healthCards}>
                        <View style={styles.healthCard}>
                            <MaterialIcons name="monitor-weight" size={24} color={COLORS.primary} />
                            <Text style={styles.healthValue}>{healthMetrics.weight} kg</Text>
                            <Text style={styles.healthLabel}>Cân nặng</Text>
                        </View>

                        <View style={styles.healthCard}>
                            <MaterialIcons name="height" size={24} color={COLORS.primary} />
                            <Text style={styles.healthValue}>{healthMetrics.height} cm</Text>
                            <Text style={styles.healthLabel}>Chiều cao</Text>
                        </View>

                        <View style={styles.healthCard}>
                            <MaterialIcons name="analytics" size={24} color={getBMIStatus(healthMetrics.bmi).color} />
                            <Text style={[styles.healthValue, { color: getBMIStatus(healthMetrics.bmi).color }]}>
                                {healthMetrics.bmi}
                            </Text>
                            <Text style={styles.healthLabel}>BMI</Text>
                            <Text style={[styles.bmiStatus, { color: getBMIStatus(healthMetrics.bmi).color }]}>
                                {getBMIStatus(healthMetrics.bmi).status}
                            </Text>
                        </View>
                    </View>
                </View>
            )}

            {/* Medical Conditions */}
            {medicalHistory && medicalHistory.conditions.length > 0 && (
                <View style={styles.medicalSection}>
                    <Text style={styles.sectionTitle}>Tình trạng sức khỏe</Text>
                    <View style={styles.conditionsContainer}>
                        {medicalHistory.conditions.map((condition, index) => (
                            <View key={index} style={styles.conditionChip}>
                                <MaterialIcons name="local-hospital" size={16} color={COLORS.error} />
                                <Text style={styles.conditionText}>{condition}</Text>
                            </View>
                        ))}
                    </View>
                </View>
            )}

            {/* Settings */}
            <View style={styles.settingsSection}>
                <Text style={styles.sectionTitle}>Cài đặt</Text>

                <View style={styles.settingItem}>
                    <View style={styles.settingInfo}>
                        <MaterialIcons name="notifications" size={24} color={COLORS.primary} />
                        <View style={styles.settingText}>
                            <Text style={styles.settingTitle}>Thông báo</Text>
                            <Text style={styles.settingSubtitle}>Nhận nhắc nhở và cập nhật</Text>
                        </View>
                    </View>
                    <Switch
                        value={notificationsEnabled}
                        onValueChange={setNotificationsEnabled}
                        trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                        thumbColor={notificationsEnabled ? COLORS.primary : COLORS.gray}
                    />
                </View>

                <View style={styles.settingItem}>
                    <View style={styles.settingInfo}>
                        <MaterialIcons name="dark-mode" size={24} color={COLORS.primary} />
                        <View style={styles.settingText}>
                            <Text style={styles.settingTitle}>Chế độ tối</Text>
                            <Text style={styles.settingSubtitle}>Giao diện tối cho mắt</Text>
                        </View>
                    </View>
                    <Switch
                        value={darkModeEnabled}
                        onValueChange={setDarkModeEnabled}
                        trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                        thumbColor={darkModeEnabled ? COLORS.primary : COLORS.gray}
                    />
                </View>
            </View>

            {/* Menu Items */}
            <View style={styles.menuSection}>
                {menuItems.map((item, index) => (
                    <TouchableOpacity
                        key={index}
                        style={styles.menuItem}
                        onPress={item.onPress}
                    >
                        <View style={styles.menuItemContent}>
                            <View style={styles.menuIcon}>
                                <MaterialIcons name={item.icon as any} size={24} color={COLORS.primary} />
                            </View>
                            <View style={styles.menuText}>
                                <Text style={styles.menuTitle}>{item.title}</Text>
                                <Text style={styles.menuSubtitle}>{item.subtitle}</Text>
                            </View>
                            <MaterialIcons name="chevron-right" size={24} color={COLORS.gray} />
                        </View>
                    </TouchableOpacity>
                ))}
            </View>

            {/* App Info */}
            <View style={styles.appInfo}>
                <Text style={styles.appVersion}>Food Advisor v1.0.0</Text>
                <Text style={styles.appDescription}>
                    Ứng dụng tư vấn dinh dưỡng thông minh
                </Text>
            </View>

            {/* Logout Button */}
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                <MaterialIcons name="logout" size={20} color={COLORS.error} />
                <Text style={styles.logoutText}>Đăng xuất</Text>
            </TouchableOpacity>

            <View style={styles.bottomSpacing} />
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        paddingTop: 20,
        paddingBottom: 30,
        paddingHorizontal: 20,
    },
    profileInfo: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    avatar: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    userInfo: {
        flex: 1,
        marginLeft: 15,
    },
    userName: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.white,
    },
    userEmail: {
        fontSize: 14,
        color: COLORS.white,
        opacity: 0.9,
        marginTop: 4,
    },
    editButton: {
        padding: 8,
    },
    healthSummary: {
        padding: 20,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 15,
    },
    healthCards: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    healthCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        alignItems: 'center',
        flex: 1,
        marginHorizontal: 5,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    healthValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginTop: 8,
    },
    healthLabel: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: 4,
    },
    bmiStatus: {
        fontSize: 10,
        fontWeight: 'bold',
        marginTop: 2,
    },
    medicalSection: {
        paddingHorizontal: 20,
        paddingBottom: 20,
    },
    conditionsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    conditionChip: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFEBEE',
        borderRadius: 20,
        paddingHorizontal: 12,
        paddingVertical: 6,
        margin: 4,
    },
    conditionText: {
        color: COLORS.error,
        fontSize: 12,
        marginLeft: 6,
        fontWeight: '500',
    },
    settingsSection: {
        paddingHorizontal: 20,
        paddingBottom: 20,
    },
    settingItem: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    settingInfo: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    settingText: {
        marginLeft: 15,
        flex: 1,
    },
    settingTitle: {
        fontSize: 16,
        fontWeight: '500',
        color: COLORS.textPrimary,
    },
    settingSubtitle: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 2,
    },
    menuSection: {
        paddingHorizontal: 20,
    },
    menuItem: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    menuItemContent: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 15,
    },
    menuIcon: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.primaryLighter,
        justifyContent: 'center',
        alignItems: 'center',
    },
    menuText: {
        flex: 1,
        marginLeft: 15,
    },
    menuTitle: {
        fontSize: 16,
        fontWeight: '500',
        color: COLORS.textPrimary,
    },
    menuSubtitle: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 2,
    },
    appInfo: {
        alignItems: 'center',
        paddingVertical: 30,
    },
    appVersion: {
        fontSize: 14,
        color: COLORS.textSecondary,
        fontWeight: '500',
    },
    appDescription: {
        fontSize: 12,
        color: COLORS.gray,
        marginTop: 4,
    },
    logoutButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: COLORS.white,
        borderWidth: 2,
        borderColor: COLORS.error,
        borderRadius: 25,
        paddingVertical: 15,
        marginHorizontal: 20,
        marginBottom: 20,
    },
    logoutText: {
        color: COLORS.error,
        fontSize: 16,
        fontWeight: 'bold',
        marginLeft: 8,
    },
    bottomSpacing: {
        height: 20,
    },
});