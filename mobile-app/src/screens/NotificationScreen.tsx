import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    Switch,
    Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import * as Notifications from 'expo-notifications';
import { apiService } from '../services/apiService';
import { COLORS } from '../constants/colors';

interface NotificationItem {
    id: string;
    title: string;
    message: string;
    type: 'meal' | 'medication' | 'health' | 'reminder' | 'system';
    timestamp: Date;
    isRead: boolean;
}

const NotificationScreen = ({ navigation }: any) => {
    const [notifications, setNotifications] = useState<NotificationItem[]>([]);
    const [settings, setSettings] = useState({
        mealReminders: true,
        medicationReminders: true,
        healthTips: true,
        weeklyReports: true,
        systemNotifications: true,
    });

    useEffect(() => {
        loadNotifications();
        requestPermissions();
    }, []);

    const requestPermissions = async () => {
        const { status } = await Notifications.requestPermissionsAsync();
        if (status !== 'granted') {
            Alert.alert(
                'Quyền thông báo',
                'Ứng dụng cần quyền gửi thông báo để nhắc nhở bạn về các hoạt động sức khỏe.',
                [
                    { text: 'Bỏ qua', style: 'cancel' },
                    { text: 'Cài đặt', onPress: () => Notifications.requestPermissionsAsync() },
                ]
            );
        }
    };

    const loadNotifications = async () => {
        try {
            const response = await apiService.getNotifications();
            if (response.success && response.data) {
                setNotifications(response.data);
            }
        } catch (error) {
            // Load mock data for demo
            const mockNotifications: NotificationItem[] = [
                {
                    id: '1',
                    title: 'Nhắc nhở bữa sáng',
                    message: 'Đã đến giờ ăn sáng! Hãy chọn những thực phẩm giàu protein và chất xơ.',
                    type: 'meal',
                    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                    isRead: false,
                },
                {
                    id: '2',
                    title: 'Uống thuốc',
                    message: 'Đã đến giờ uống thuốc huyết áp. Nhớ uống cùng với nước.',
                    type: 'medication',
                    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
                    isRead: true,
                },
                {
                    id: '3',
                    title: 'Lời khuyên sức khỏe',
                    message: 'Hãy uống ít nhất 8 ly nước mỗi ngày để duy trì sức khỏe tốt.',
                    type: 'health',
                    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
                    isRead: true,
                },
                {
                    id: '4',
                    title: 'Báo cáo tuần',
                    message: 'Báo cáo dinh dưỡng tuần này đã sẵn sàng. Bạn đã đạt 85% mục tiêu.',
                    type: 'system',
                    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
                    isRead: false,
                },
            ];
            setNotifications(mockNotifications);
        }
    };

    const markAsRead = async (notificationId: string) => {
        try {
            await apiService.markNotificationRead(notificationId);
            setNotifications(prev =>
                prev.map(notif =>
                    notif.id === notificationId ? { ...notif, isRead: true } : notif
                )
            );
        } catch (error) {
            // Update locally for demo
            setNotifications(prev =>
                prev.map(notif =>
                    notif.id === notificationId ? { ...notif, isRead: true } : notif
                )
            );
        }
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'meal': return 'restaurant';
            case 'medication': return 'medication';
            case 'health': return 'favorite';
            case 'reminder': return 'alarm';
            case 'system': return 'info';
            default: return 'notifications';
        }
    };

    const getNotificationColor = (type: string) => {
        switch (type) {
            case 'meal': return COLORS.primary;
            case 'medication': return COLORS.error;
            case 'health': return COLORS.success;
            case 'reminder': return COLORS.warning;
            case 'system': return COLORS.info;
            default: return COLORS.gray;
        }
    };

    const formatTime = (date: Date) => {
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

        if (diffInHours < 1) {
            const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
            return `${diffInMinutes} phút trước`;
        } else if (diffInHours < 24) {
            return `${diffInHours} giờ trước`;
        } else {
            const diffInDays = Math.floor(diffInHours / 24);
            return `${diffInDays} ngày trước`;
        }
    };

    const scheduleNotification = async (type: string, title: string, body: string, trigger: any) => {
        try {
            await Notifications.scheduleNotificationAsync({
                content: {
                    title,
                    body,
                    sound: true,
                },
                trigger,
            });
        } catch (error) {
            console.error('Error scheduling notification:', error);
        }
    };

    const updateSetting = (key: string, value: boolean) => {
        setSettings(prev => ({ ...prev, [key]: value }));

        // Schedule or cancel notifications based on settings
        if (value) {
            switch (key) {
                case 'mealReminders':
                    // Schedule meal reminders
                    scheduleNotification(
                        'meal',
                        'Nhắc nhở bữa ăn',
                        'Đã đến giờ ăn! Hãy chọn thực phẩm phù hợp với sức khỏe của bạn.',
                        { hour: 7, minute: 0, repeats: true }
                    );
                    break;
                case 'medicationReminders':
                    // Schedule medication reminders
                    scheduleNotification(
                        'medication',
                        'Nhắc nhở uống thuốc',
                        'Đã đến giờ uống thuốc. Đừng quên!',
                        { hour: 8, minute: 0, repeats: true }
                    );
                    break;
                case 'healthTips':
                    // Schedule daily health tips
                    scheduleNotification(
                        'health',
                        'Lời khuyên sức khỏe',
                        'Mẹo sức khỏe hàng ngày dành cho bạn.',
                        { hour: 9, minute: 0, repeats: true }
                    );
                    break;
            }
        }
    };

    return (
        <View style={styles.container}>
            <LinearGradient
                colors={[COLORS.gradientStart, COLORS.gradientEnd]}
                style={styles.header}
            >
                <View style={styles.headerContent}>
                    <TouchableOpacity
                        style={styles.backButton}
                        onPress={() => navigation.goBack()}
                    >
                        <Icon name="arrow-back" size={24} color={COLORS.white} />
                    </TouchableOpacity>
                    <Text style={styles.headerTitle}>Thông báo</Text>
                    <TouchableOpacity style={styles.settingsButton}>
                        <Icon name="settings" size={24} color={COLORS.white} />
                    </TouchableOpacity>
                </View>
            </LinearGradient>

            <ScrollView style={styles.content}>
                {/* Notification Settings */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Cài đặt thông báo</Text>

                    <View style={styles.settingItem}>
                        <View style={styles.settingInfo}>
                            <Icon name="restaurant" size={24} color={COLORS.primary} />
                            <View style={styles.settingText}>
                                <Text style={styles.settingTitle}>Nhắc nhở bữa ăn</Text>
                                <Text style={styles.settingSubtitle}>Nhắc nhở giờ ăn và gợi ý thực đơn</Text>
                            </View>
                        </View>
                        <Switch
                            value={settings.mealReminders}
                            onValueChange={(value) => updateSetting('mealReminders', value)}
                            trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                            thumbColor={settings.mealReminders ? COLORS.primary : COLORS.gray}
                        />
                    </View>

                    <View style={styles.settingItem}>
                        <View style={styles.settingInfo}>
                            <Icon name="medication" size={24} color={COLORS.error} />
                            <View style={styles.settingText}>
                                <Text style={styles.settingTitle}>Nhắc nhở uống thuốc</Text>
                                <Text style={styles.settingSubtitle}>Nhắc nhở giờ uống thuốc theo đơn</Text>
                            </View>
                        </View>
                        <Switch
                            value={settings.medicationReminders}
                            onValueChange={(value) => updateSetting('medicationReminders', value)}
                            trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                            thumbColor={settings.medicationReminders ? COLORS.primary : COLORS.gray}
                        />
                    </View>

                    <View style={styles.settingItem}>
                        <View style={styles.settingInfo}>
                            <Icon name="favorite" size={24} color={COLORS.success} />
                            <View style={styles.settingText}>
                                <Text style={styles.settingTitle}>Lời khuyên sức khỏe</Text>
                                <Text style={styles.settingSubtitle}>Mẹo và lời khuyên dinh dưỡng hàng ngày</Text>
                            </View>
                        </View>
                        <Switch
                            value={settings.healthTips}
                            onValueChange={(value) => updateSetting('healthTips', value)}
                            trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                            thumbColor={settings.healthTips ? COLORS.primary : COLORS.gray}
                        />
                    </View>

                    <View style={styles.settingItem}>
                        <View style={styles.settingInfo}>
                            <Icon name="analytics" size={24} color={COLORS.info} />
                            <View style={styles.settingText}>
                                <Text style={styles.settingTitle}>Báo cáo tuần</Text>
                                <Text style={styles.settingSubtitle}>Tổng kết dinh dưỡng và sức khỏe</Text>
                            </View>
                        </View>
                        <Switch
                            value={settings.weeklyReports}
                            onValueChange={(value) => updateSetting('weeklyReports', value)}
                            trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                            thumbColor={settings.weeklyReports ? COLORS.primary : COLORS.gray}
                        />
                    </View>

                    <View style={styles.settingItem}>
                        <View style={styles.settingInfo}>
                            <Icon name="info" size={24} color={COLORS.gray} />
                            <View style={styles.settingText}>
                                <Text style={styles.settingTitle}>Thông báo hệ thống</Text>
                                <Text style={styles.settingSubtitle}>Cập nhật ứng dụng và tính năng mới</Text>
                            </View>
                        </View>
                        <Switch
                            value={settings.systemNotifications}
                            onValueChange={(value) => updateSetting('systemNotifications', value)}
                            trackColor={{ false: COLORS.lightGray, true: COLORS.primaryLight }}
                            thumbColor={settings.systemNotifications ? COLORS.primary : COLORS.gray}
                        />
                    </View>
                </View>

                {/* Recent Notifications */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Thông báo gần đây</Text>

                    {notifications.length === 0 ? (
                        <View style={styles.emptyState}>
                            <Icon name="notifications-none" size={64} color={COLORS.gray} />
                            <Text style={styles.emptyStateText}>Chưa có thông báo nào</Text>
                        </View>
                    ) : (
                        notifications.map((notification) => (
                            <TouchableOpacity
                                key={notification.id}
                                style={[
                                    styles.notificationItem,
                                    !notification.isRead && styles.unreadNotification
                                ]}
                                onPress={() => markAsRead(notification.id)}
                            >
                                <View style={styles.notificationIcon}>
                                    <Icon
                                        name={getNotificationIcon(notification.type)}
                                        size={24}
                                        color={getNotificationColor(notification.type)}
                                    />
                                </View>

                                <View style={styles.notificationContent}>
                                    <View style={styles.notificationHeader}>
                                        <Text style={styles.notificationTitle}>
                                            {notification.title}
                                        </Text>
                                        <Text style={styles.notificationTime}>
                                            {formatTime(notification.timestamp)}
                                        </Text>
                                    </View>
                                    <Text style={styles.notificationMessage}>
                                        {notification.message}
                                    </Text>
                                </View>

                                {!notification.isRead && (
                                    <View style={styles.unreadDot} />
                                )}
                            </TouchableOpacity>
                        ))
                    )}
                </View>
            </ScrollView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        paddingTop: 10,
        paddingBottom: 20,
        paddingHorizontal: 20,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    backButton: {
        padding: 5,
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.white,
        flex: 1,
        textAlign: 'center',
    },
    settingsButton: {
        padding: 5,
    },
    content: {
        flex: 1,
    },
    section: {
        padding: 20,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 15,
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
    emptyState: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 40,
    },
    emptyStateText: {
        fontSize: 16,
        color: COLORS.textSecondary,
        marginTop: 15,
    },
    notificationItem: {
        flexDirection: 'row',
        alignItems: 'flex-start',
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
    unreadNotification: {
        borderLeftWidth: 4,
        borderLeftColor: COLORS.primary,
    },
    notificationIcon: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.background,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 15,
    },
    notificationContent: {
        flex: 1,
    },
    notificationHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 5,
    },
    notificationTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.textPrimary,
        flex: 1,
    },
    notificationTime: {
        fontSize: 12,
        color: COLORS.textSecondary,
    },
    notificationMessage: {
        fontSize: 14,
        color: COLORS.textSecondary,
        lineHeight: 20,
    },
    unreadDot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: COLORS.primary,
        marginLeft: 10,
        marginTop: 5,
    },
});

export default NotificationScreen;