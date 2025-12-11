import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    Dimensions,
    RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import { LineChart, PieChart } from 'react-native-chart-kit';
import { useAuth } from '../contexts/AuthContext';
import { useHealth } from '../contexts/HealthContext';
import { COLORS } from '../constants/colors';

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }: any) => {
    const { user } = useAuth();
    const { healthMetrics, nutritionGoals, getDailyNutritionSummary } = useHealth();
    const [dailyNutrition, setDailyNutrition] = useState<any>(null);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadDailyData();
    }, []);

    const loadDailyData = async () => {
        const today = new Date().toISOString().split('T')[0];
        const nutrition = await getDailyNutritionSummary(today);
        setDailyNutrition(nutrition);
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadDailyData();
        setRefreshing(false);
    };

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Chào buổi sáng';
        if (hour < 18) return 'Chào buổi chiều';
        return 'Chào buổi tối';
    };

    const getBMIStatus = (bmi: number) => {
        if (bmi < 18.5) return { status: 'Thiếu cân', color: COLORS.warning };
        if (bmi < 25) return { status: 'Bình thường', color: COLORS.success };
        if (bmi < 30) return { status: 'Thừa cân', color: COLORS.warning };
        return { status: 'Béo phì', color: COLORS.error };
    };

    const nutritionData = dailyNutrition ? [
        {
            name: 'Protein',
            population: dailyNutrition.protein || 0,
            color: COLORS.chartBlue,
            legendFontColor: COLORS.textPrimary,
            legendFontSize: 12,
        },
        {
            name: 'Carbs',
            population: dailyNutrition.carbs || 0,
            color: COLORS.chartOrange,
            legendFontColor: COLORS.textPrimary,
            legendFontSize: 12,
        },
        {
            name: 'Fat',
            population: dailyNutrition.fat || 0,
            color: COLORS.chartRed,
            legendFontColor: COLORS.textPrimary,
            legendFontSize: 12,
        },
    ] : [];

    const weeklyCaloriesData = {
        labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
        datasets: [
            {
                data: [1800, 2100, 1950, 2200, 1900, 2300, 2000],
                color: (opacity = 1) => `rgba(46, 125, 50, ${opacity})`,
                strokeWidth: 2,
            },
        ],
    };

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            {/* Header */}
            <LinearGradient
                colors={[COLORS.gradientStart, COLORS.gradientEnd]}
                style={styles.header}
            >
                <View style={styles.headerContent}>
                    <View>
                        <Text style={styles.greeting}>{getGreeting()}</Text>
                        <Text style={styles.userName}>{user?.name || 'Người dùng'}</Text>
                    </View>
                    <TouchableOpacity
                        style={styles.notificationButton}
                        onPress={() => navigation.navigate('Notifications')}
                    >
                        <Icon name="notifications" size={24} color={COLORS.white} />
                    </TouchableOpacity>
                </View>
            </LinearGradient>

            {/* Quick Actions */}
            <View style={styles.quickActions}>
                <TouchableOpacity
                    style={styles.actionCard}
                    onPress={() => navigation.navigate('Camera')}
                >
                    <Icon name="camera-alt" size={32} color={COLORS.primary} />
                    <Text style={styles.actionText}>Tính Calo</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.actionCard}
                    onPress={() => navigation.navigate('Chat')}
                >
                    <Icon name="chat" size={32} color={COLORS.primary} />
                    <Text style={styles.actionText}>Tư vấn</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.actionCard}
                    onPress={() => navigation.navigate('Recipe')}
                >
                    <Icon name="restaurant" size={32} color={COLORS.primary} />
                    <Text style={styles.actionText}>Công thức</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.actionCard}
                    onPress={() => navigation.navigate('HealthInfo')}
                >
                    <Icon name="favorite" size={32} color={COLORS.primary} />
                    <Text style={styles.actionText}>Sức khỏe</Text>
                </TouchableOpacity>
            </View>

            {/* Health Metrics */}
            {healthMetrics && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Chỉ số sức khỏe</Text>
                    <View style={styles.metricsContainer}>
                        <View style={styles.metricCard}>
                            <Icon name="monitor-weight" size={24} color={COLORS.primary} />
                            <Text style={styles.metricValue}>{healthMetrics.weight} kg</Text>
                            <Text style={styles.metricLabel}>Cân nặng</Text>
                        </View>

                        <View style={styles.metricCard}>
                            <Icon name="height" size={24} color={COLORS.primary} />
                            <Text style={styles.metricValue}>{healthMetrics.height} cm</Text>
                            <Text style={styles.metricLabel}>Chiều cao</Text>
                        </View>

                        <View style={styles.metricCard}>
                            <Icon name="analytics" size={24} color={getBMIStatus(healthMetrics.bmi).color} />
                            <Text style={[styles.metricValue, { color: getBMIStatus(healthMetrics.bmi).color }]}>
                                {healthMetrics.bmi}
                            </Text>
                            <Text style={styles.metricLabel}>BMI</Text>
                            <Text style={[styles.bmiStatus, { color: getBMIStatus(healthMetrics.bmi).color }]}>
                                {getBMIStatus(healthMetrics.bmi).status}
                            </Text>
                        </View>
                    </View>
                </View>
            )}

            {/* Daily Nutrition */}
            {dailyNutrition && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Dinh dưỡng hôm nay</Text>
                    <View style={styles.nutritionCard}>
                        <View style={styles.caloriesInfo}>
                            <Text style={styles.caloriesConsumed}>
                                {dailyNutrition.totalCalories || 0}
                            </Text>
                            <Text style={styles.caloriesLabel}>/ {nutritionGoals?.dailyCalories || 2000} kcal</Text>
                        </View>

                        {nutritionData.length > 0 && (
                            <PieChart
                                data={nutritionData}
                                width={width - 80}
                                height={180}
                                chartConfig={{
                                    color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                                }}
                                accessor="population"
                                backgroundColor="transparent"
                                paddingLeft="15"
                                absolute
                            />
                        )}
                    </View>
                </View>
            )}

            {/* Weekly Calories Chart */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Calo tuần này</Text>
                <View style={styles.chartCard}>
                    <LineChart
                        data={weeklyCaloriesData}
                        width={width - 60}
                        height={200}
                        chartConfig={{
                            backgroundColor: COLORS.white,
                            backgroundGradientFrom: COLORS.white,
                            backgroundGradientTo: COLORS.white,
                            decimalPlaces: 0,
                            color: (opacity = 1) => `rgba(46, 125, 50, ${opacity})`,
                            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                            style: {
                                borderRadius: 16,
                            },
                            propsForDots: {
                                r: '6',
                                strokeWidth: '2',
                                stroke: COLORS.primary,
                            },
                        }}
                        bezier
                        style={styles.chart}
                    />
                </View>
            </View>

            {/* Health Tips */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Lời khuyên sức khỏe</Text>
                <View style={styles.tipCard}>
                    <Icon name="lightbulb" size={24} color={COLORS.warning} />
                    <View style={styles.tipContent}>
                        <Text style={styles.tipTitle}>Uống đủ nước</Text>
                        <Text style={styles.tipText}>
                            Hãy uống ít nhất 8 ly nước mỗi ngày để duy trì sức khỏe tốt
                        </Text>
                    </View>
                </View>

                <View style={styles.tipCard}>
                    <Icon name="fitness-center" size={24} color={COLORS.primary} />
                    <View style={styles.tipContent}>
                        <Text style={styles.tipTitle}>Tập thể dục đều đặn</Text>
                        <Text style={styles.tipText}>
                            30 phút tập thể dục mỗi ngày giúp cải thiện sức khỏe tim mạch
                        </Text>
                    </View>
                </View>
            </View>
        </ScrollView>
    );
};

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
    headerContent: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    greeting: {
        fontSize: 16,
        color: COLORS.white,
        opacity: 0.9,
    },
    userName: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.white,
        marginTop: 4,
    },
    notificationButton: {
        padding: 8,
    },
    quickActions: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingHorizontal: 20,
        marginTop: -15,
    },
    actionCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        alignItems: 'center',
        width: (width - 60) / 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    actionText: {
        fontSize: 12,
        color: COLORS.textPrimary,
        marginTop: 8,
        textAlign: 'center',
    },
    section: {
        marginTop: 30,
        paddingHorizontal: 20,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 15,
    },
    metricsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    metricCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        alignItems: 'center',
        width: (width - 60) / 3,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    metricValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginTop: 8,
    },
    metricLabel: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: 4,
    },
    bmiStatus: {
        fontSize: 10,
        fontWeight: 'bold',
        marginTop: 2,
    },
    nutritionCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    caloriesInfo: {
        flexDirection: 'row',
        alignItems: 'baseline',
        justifyContent: 'center',
        marginBottom: 20,
    },
    caloriesConsumed: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    caloriesLabel: {
        fontSize: 16,
        color: COLORS.textSecondary,
        marginLeft: 8,
    },
    chartCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    chart: {
        borderRadius: 16,
    },
    tipCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        flexDirection: 'row',
        alignItems: 'flex-start',
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    tipContent: {
        flex: 1,
        marginLeft: 15,
    },
    tipTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 4,
    },
    tipText: {
        fontSize: 14,
        color: COLORS.textSecondary,
        lineHeight: 20,
    },
});

export default HomeScreen;