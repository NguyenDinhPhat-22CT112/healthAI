import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configure notification behavior
Notifications.setNotificationHandler({
    handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: false,
    }),
});

export interface NotificationSchedule {
    id: string;
    title: string;
    body: string;
    trigger: Notifications.NotificationTriggerInput;
    data?: any;
}

class NotificationService {
    private static instance: NotificationService;
    private scheduledNotifications: Map<string, string> = new Map();

    static getInstance(): NotificationService {
        if (!NotificationService.instance) {
            NotificationService.instance = new NotificationService();
        }
        return NotificationService.instance;
    }

    async requestPermissions(): Promise<boolean> {
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        if (existingStatus !== 'granted') {
            const { status } = await Notifications.requestPermissionsAsync();
            finalStatus = status;
        }

        return finalStatus === 'granted';
    }

    async scheduleMealReminders(enabled: boolean): Promise<void> {
        if (!enabled) {
            await this.cancelNotificationsByType('meal');
            return;
        }

        const mealSchedules: NotificationSchedule[] = [
            {
                id: 'breakfast-reminder',
                title: 'Nhắc nhở bữa sáng',
                body: 'Đã đến giờ ăn sáng! Hãy chọn những thực phẩm giàu protein và chất xơ.',
                trigger: {
                    hour: 7,
                    minute: 0,
                    repeats: true,
                },
                data: { type: 'meal', meal: 'breakfast' },
            },
            {
                id: 'lunch-reminder',
                title: 'Nhắc nhở bữa trưa',
                body: 'Đã đến giờ ăn trưa! Đừng quên bổ sung rau xanh và protein.',
                trigger: {
                    hour: 12,
                    minute: 0,
                    repeats: true,
                },
                data: { type: 'meal', meal: 'lunch' },
            },
            {
                id: 'dinner-reminder',
                title: 'Nhắc nhở bữa tối',
                body: 'Đã đến giờ ăn tối! Hãy ăn nhẹ và tránh thức ăn nặng.',
                trigger: {
                    hour: 18,
                    minute: 30,
                    repeats: true,
                },
                data: { type: 'meal', meal: 'dinner' },
            },
        ];

        for (const schedule of mealSchedules) {
            await this.scheduleNotification(schedule);
        }
    }

    async scheduleMedicationReminders(medications: any[], enabled: boolean): Promise<void> {
        if (!enabled) {
            await this.cancelNotificationsByType('medication');
            return;
        }

        for (const medication of medications) {
            const schedules: NotificationSchedule[] = medication.times.map((time: string, index: number) => ({
                id: `medication-${medication.id}-${index}`,
                title: 'Nhắc nhở uống thuốc',
                body: `Đã đến giờ uống ${medication.name}. Liều lượng: ${medication.dosage}`,
                trigger: {
                    hour: parseInt(time.split(':')[0]),
                    minute: parseInt(time.split(':')[1]),
                    repeats: true,
                },
                data: {
                    type: 'medication',
                    medicationId: medication.id,
                    medicationName: medication.name
                },
            }));

            for (const schedule of schedules) {
                await this.scheduleNotification(schedule);
            }
        }
    }

    async scheduleHealthTips(enabled: boolean): Promise<void> {
        if (!enabled) {
            await this.cancelNotificationsByType('health-tip');
            return;
        }

        const healthTips = [
            'Uống ít nhất 8 ly nước mỗi ngày để duy trì sức khỏe tốt.',
            'Tập thể dục 30 phút mỗi ngày giúp cải thiện sức khỏe tim mạch.',
            'Ăn nhiều rau xanh và trái cây để bổ sung vitamin và khoáng chất.',
            'Ngủ đủ 7-8 tiếng mỗi đêm để cơ thể phục hồi.',
            'Hạn chế đường và muối trong chế độ ăn hàng ngày.',
            'Đi bộ sau bữa ăn giúp tiêu hóa tốt hơn.',
            'Ăn chậm và nhai kỹ để hỗ trợ tiêu hóa.',
        ];

        const schedule: NotificationSchedule = {
            id: 'daily-health-tip',
            title: 'Lời khuyên sức khỏe',
            body: healthTips[Math.floor(Math.random() * healthTips.length)],
            trigger: {
                hour: 9,
                minute: 0,
                repeats: true,
            },
            data: { type: 'health-tip' },
        };

        await this.scheduleNotification(schedule);
    }

    async scheduleWeeklyReports(enabled: boolean): Promise<void> {
        if (!enabled) {
            await this.cancelNotificationsByType('weekly-report');
            return;
        }

        const schedule: NotificationSchedule = {
            id: 'weekly-report',
            title: 'Báo cáo dinh dưỡng tuần',
            body: 'Báo cáo tổng kết dinh dưỡng và sức khỏe tuần này đã sẵn sàng!',
            trigger: {
                weekday: 1, // Monday
                hour: 10,
                minute: 0,
                repeats: true,
            },
            data: { type: 'weekly-report' },
        };

        await this.scheduleNotification(schedule);
    }

    async scheduleWaterReminders(enabled: boolean, intervals: number[] = [9, 11, 14, 16, 19]): Promise<void> {
        if (!enabled) {
            await this.cancelNotificationsByType('water');
            return;
        }

        const schedules: NotificationSchedule[] = intervals.map((hour, index) => ({
            id: `water-reminder-${index}`,
            title: 'Nhắc nhở uống nước',
            body: 'Đã đến giờ uống nước! Hãy uống một ly nước để duy trì sức khỏe.',
            trigger: {
                hour,
                minute: 0,
                repeats: true,
            },
            data: { type: 'water' },
        }));

        for (const schedule of schedules) {
            await this.scheduleNotification(schedule);
        }
    }

    async scheduleCustomReminder(
        title: string,
        body: string,
        trigger: Notifications.NotificationTriggerInput,
        data?: any
    ): Promise<string> {
        const id = `custom-${Date.now()}`;
        const schedule: NotificationSchedule = {
            id,
            title,
            body,
            trigger,
            data: { ...data, type: 'custom' },
        };

        await this.scheduleNotification(schedule);
        return id;
    }

    private async scheduleNotification(schedule: NotificationSchedule): Promise<void> {
        try {
            const notificationId = await Notifications.scheduleNotificationAsync({
                content: {
                    title: schedule.title,
                    body: schedule.body,
                    data: schedule.data,
                    sound: true,
                },
                trigger: schedule.trigger,
            });

            this.scheduledNotifications.set(schedule.id, notificationId);
            await this.saveScheduledNotifications();
        } catch (error) {
            console.error('Error scheduling notification:', error);
        }
    }

    async cancelNotification(id: string): Promise<void> {
        const notificationId = this.scheduledNotifications.get(id);
        if (notificationId) {
            await Notifications.cancelScheduledNotificationAsync(notificationId);
            this.scheduledNotifications.delete(id);
            await this.saveScheduledNotifications();
        }
    }

    async cancelNotificationsByType(type: string): Promise<void> {
        const toCancel: string[] = [];

        for (const [id] of this.scheduledNotifications) {
            if (id.includes(type)) {
                toCancel.push(id);
            }
        }

        for (const id of toCancel) {
            await this.cancelNotification(id);
        }
    }

    async cancelAllNotifications(): Promise<void> {
        await Notifications.cancelAllScheduledNotificationsAsync();
        this.scheduledNotifications.clear();
        await this.saveScheduledNotifications();
    }

    async getScheduledNotifications(): Promise<Notifications.NotificationRequest[]> {
        return await Notifications.getAllScheduledNotificationsAsync();
    }

    private async saveScheduledNotifications(): Promise<void> {
        try {
            const data = JSON.stringify(Array.from(this.scheduledNotifications.entries()));
            await AsyncStorage.setItem('scheduledNotifications', data);
        } catch (error) {
            console.error('Error saving scheduled notifications:', error);
        }
    }

    private async loadScheduledNotifications(): Promise<void> {
        try {
            const data = await AsyncStorage.getItem('scheduledNotifications');
            if (data) {
                const entries = JSON.parse(data);
                this.scheduledNotifications = new Map(entries);
            }
        } catch (error) {
            console.error('Error loading scheduled notifications:', error);
        }
    }

    async initialize(): Promise<void> {
        await this.loadScheduledNotifications();
        await this.requestPermissions();
    }

    // Handle notification responses
    addNotificationResponseListener(
        listener: (response: Notifications.NotificationResponse) => void
    ): Notifications.Subscription {
        return Notifications.addNotificationResponseReceivedListener(listener);
    }

    // Handle notifications received while app is in foreground
    addNotificationReceivedListener(
        listener: (notification: Notifications.Notification) => void
    ): Notifications.Subscription {
        return Notifications.addNotificationReceivedListener(listener);
    }
}

export default NotificationService.getInstance();