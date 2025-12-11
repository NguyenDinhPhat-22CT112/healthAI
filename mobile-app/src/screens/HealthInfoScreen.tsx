import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    TextInput,
    Alert,
    ActivityIndicator,
    Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import { useHealth } from '../contexts/HealthContext';
import { COLORS } from '../constants/colors';

const HealthInfoScreen = ({ navigation }: any) => {
    const {
        healthMetrics,
        medicalHistory,
        nutritionGoals,
        updateHealthMetrics,
        updateMedicalHistory,
        updateNutritionGoals,
        isLoading
    } = useHealth();

    const [activeTab, setActiveTab] = useState<'metrics' | 'medical' | 'goals'>('metrics');
    const [isEditing, setIsEditing] = useState(false);
    const [showConditionModal, setShowConditionModal] = useState(false);
    const [showAllergyModal, setShowAllergyModal] = useState(false);

    // Health Metrics State
    const [metricsData, setMetricsData] = useState({
        weight: healthMetrics?.weight?.toString() || '',
        height: healthMetrics?.height?.toString() || '',
        bloodPressure: healthMetrics?.bloodPressure || '',
        bloodSugar: healthMetrics?.bloodSugar?.toString() || '',
        cholesterol: healthMetrics?.cholesterol?.toString() || '',
    });

    // Medical History State
    const [medicalData, setMedicalData] = useState({
        conditions: medicalHistory?.conditions || [],
        allergies: medicalHistory?.allergies || [],
        medications: medicalHistory?.medications || [],
        dietaryRestrictions: medicalHistory?.dietaryRestrictions || [],
    });

    // Nutrition Goals State
    const [goalsData, setGoalsData] = useState({
        dailyCalories: nutritionGoals?.dailyCalories?.toString() || '2000',
        protein: nutritionGoals?.protein?.toString() || '150',
        carbs: nutritionGoals?.carbs?.toString() || '250',
        fat: nutritionGoals?.fat?.toString() || '65',
        fiber: nutritionGoals?.fiber?.toString() || '25',
        sodium: nutritionGoals?.sodium?.toString() || '2300',
    });

    const [newCondition, setNewCondition] = useState('');
    const [newAllergy, setNewAllergy] = useState('');

    useEffect(() => {
        if (healthMetrics) {
            setMetricsData({
                weight: healthMetrics.weight?.toString() || '',
                height: healthMetrics.height?.toString() || '',
                bloodPressure: healthMetrics.bloodPressure || '',
                bloodSugar: healthMetrics.bloodSugar?.toString() || '',
                cholesterol: healthMetrics.cholesterol?.toString() || '',
            });
        }
    }, [healthMetrics]);

    const handleSave = async () => {
        try {
            let success = true;

            if (activeTab === 'metrics') {
                const metrics = {
                    weight: parseFloat(metricsData.weight) || 0,
                    height: parseFloat(metricsData.height) || 0,
                    bloodPressure: metricsData.bloodPressure,
                    bloodSugar: parseFloat(metricsData.bloodSugar) || undefined,
                    cholesterol: parseFloat(metricsData.cholesterol) || undefined,
                };
                success = await updateHealthMetrics(metrics);
            } else if (activeTab === 'medical') {
                success = await updateMedicalHistory(medicalData);
            } else if (activeTab === 'goals') {
                const goals = {
                    dailyCalories: parseInt(goalsData.dailyCalories) || 2000,
                    protein: parseInt(goalsData.protein) || 150,
                    carbs: parseInt(goalsData.carbs) || 250,
                    fat: parseInt(goalsData.fat) || 65,
                    fiber: parseInt(goalsData.fiber) || 25,
                    sodium: parseInt(goalsData.sodium) || 2300,
                };
                success = await updateNutritionGoals(goals);
            }

            if (success) {
                Alert.alert('Thành công', 'Đã cập nhật thông tin');
                setIsEditing(false);
            } else {
                Alert.alert('Lỗi', 'Không thể cập nhật thông tin');
            }
        } catch (error) {
            Alert.alert('Lỗi', 'Có lỗi xảy ra khi cập nhật');
        }
    };

    const addCondition = () => {
        if (newCondition.trim() && !medicalData.conditions.includes(newCondition.trim())) {
            setMedicalData({
                ...medicalData,
                conditions: [...medicalData.conditions, newCondition.trim()],
            });
            setNewCondition('');
            setShowConditionModal(false);
        }
    };

    const removeCondition = (condition: string) => {
        setMedicalData({
            ...medicalData,
            conditions: medicalData.conditions.filter(c => c !== condition),
        });
    };

    const addAllergy = () => {
        if (newAllergy.trim() && !medicalData.allergies.includes(newAllergy.trim())) {
            setMedicalData({
                ...medicalData,
                allergies: [...medicalData.allergies, newAllergy.trim()],
            });
            setNewAllergy('');
            setShowAllergyModal(false);
        }
    };

    const removeAllergy = (allergy: string) => {
        setMedicalData({
            ...medicalData,
            allergies: medicalData.allergies.filter(a => a !== allergy),
        });
    };

    const commonConditions = [
        'Tiểu đường type 2',
        'Cao huyết áp',
        'Bệnh tim mạch',
        'Cholesterol cao',
        'Béo phì',
        'Bệnh thận',
        'Bệnh gan',
        'Gout',
        'Loãng xương',
        'Dạ dày',
    ];

    const commonAllergies = [
        'Tôm cua',
        'Sữa',
        'Trứng',
        'Đậu phộng',
        'Hạt',
        'Cá',
        'Đậu nành',
        'Lúa mì',
        'Mè',
        'Kiwi',
    ];

    const renderMetricsTab = () => (
        <View style={styles.tabContent}>
            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Cân nặng (kg)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={metricsData.weight}
                    onChangeText={(text) => setMetricsData({ ...metricsData, weight: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="Nhập cân nặng"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Chiều cao (cm)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={metricsData.height}
                    onChangeText={(text) => setMetricsData({ ...metricsData, height: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="Nhập chiều cao"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Huyết áp (mmHg)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={metricsData.bloodPressure}
                    onChangeText={(text) => setMetricsData({ ...metricsData, bloodPressure: text })}
                    editable={isEditing}
                    placeholder="VD: 120/80"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Đường huyết (mg/dL)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={metricsData.bloodSugar}
                    onChangeText={(text) => setMetricsData({ ...metricsData, bloodSugar: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="Nhập chỉ số đường huyết"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Cholesterol (mg/dL)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={metricsData.cholesterol}
                    onChangeText={(text) => setMetricsData({ ...metricsData, cholesterol: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="Nhập chỉ số cholesterol"
                />
            </View>

            {healthMetrics && metricsData.weight && metricsData.height && (
                <View style={styles.bmiCard}>
                    <Text style={styles.bmiTitle}>Chỉ số BMI</Text>
                    <Text style={styles.bmiValue}>
                        {((parseFloat(metricsData.weight) / Math.pow(parseFloat(metricsData.height) / 100, 2)) || 0).toFixed(1)}
                    </Text>
                    <Text style={styles.bmiStatus}>
                        {(() => {
                            const bmi = parseFloat(metricsData.weight) / Math.pow(parseFloat(metricsData.height) / 100, 2);
                            if (bmi < 18.5) return 'Thiếu cân';
                            if (bmi < 25) return 'Bình thường';
                            if (bmi < 30) return 'Thừa cân';
                            return 'Béo phì';
                        })()}
                    </Text>
                </View>
            )}
        </View>
    );

    const renderMedicalTab = () => (
        <View style={styles.tabContent}>
            <View style={styles.section}>
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Tình trạng bệnh lý</Text>
                    {isEditing && (
                        <TouchableOpacity
                            style={styles.addButton}
                            onPress={() => setShowConditionModal(true)}
                        >
                            <Icon name="add" size={20} color={COLORS.white} />
                        </TouchableOpacity>
                    )}
                </View>

                <View style={styles.chipContainer}>
                    {medicalData.conditions.map((condition, index) => (
                        <View key={index} style={styles.chip}>
                            <Text style={styles.chipText}>{condition}</Text>
                            {isEditing && (
                                <TouchableOpacity onPress={() => removeCondition(condition)}>
                                    <Icon name="close" size={16} color={COLORS.error} />
                                </TouchableOpacity>
                            )}
                        </View>
                    ))}
                    {medicalData.conditions.length === 0 && (
                        <Text style={styles.emptyText}>Chưa có thông tin bệnh lý</Text>
                    )}
                </View>
            </View>

            <View style={styles.section}>
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Dị ứng thực phẩm</Text>
                    {isEditing && (
                        <TouchableOpacity
                            style={styles.addButton}
                            onPress={() => setShowAllergyModal(true)}
                        >
                            <Icon name="add" size={20} color={COLORS.white} />
                        </TouchableOpacity>
                    )}
                </View>

                <View style={styles.chipContainer}>
                    {medicalData.allergies.map((allergy, index) => (
                        <View key={index} style={[styles.chip, styles.allergyChip]}>
                            <Text style={[styles.chipText, styles.allergyText]}>{allergy}</Text>
                            {isEditing && (
                                <TouchableOpacity onPress={() => removeAllergy(allergy)}>
                                    <Icon name="close" size={16} color={COLORS.warning} />
                                </TouchableOpacity>
                            )}
                        </View>
                    ))}
                    {medicalData.allergies.length === 0 && (
                        <Text style={styles.emptyText}>Chưa có thông tin dị ứng</Text>
                    )}
                </View>
            </View>
        </View>
    );

    const renderGoalsTab = () => (
        <View style={styles.tabContent}>
            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Mục tiêu calo hàng ngày</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={goalsData.dailyCalories}
                    onChangeText={(text) => setGoalsData({ ...goalsData, dailyCalories: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="2000"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Protein (g)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={goalsData.protein}
                    onChangeText={(text) => setGoalsData({ ...goalsData, protein: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="150"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Carbohydrate (g)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={goalsData.carbs}
                    onChangeText={(text) => setGoalsData({ ...goalsData, carbs: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="250"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Chất béo (g)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={goalsData.fat}
                    onChangeText={(text) => setGoalsData({ ...goalsData, fat: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="65"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Chất xơ (g)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={goalsData.fiber}
                    onChangeText={(text) => setGoalsData({ ...goalsData, fiber: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="25"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Natri (mg)</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.disabledInput]}
                    value={goalsData.sodium}
                    onChangeText={(text) => setGoalsData({ ...goalsData, sodium: text })}
                    keyboardType="numeric"
                    editable={isEditing}
                    placeholder="2300"
                />
            </View>
        </View>
    );

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
                    <Text style={styles.headerTitle}>Thông tin sức khỏe</Text>
                    <TouchableOpacity
                        style={styles.editButton}
                        onPress={() => {
                            if (isEditing) {
                                handleSave();
                            } else {
                                setIsEditing(true);
                            }
                        }}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <ActivityIndicator color={COLORS.white} size="small" />
                        ) : (
                            <Icon name={isEditing ? 'save' : 'edit'} size={24} color={COLORS.white} />
                        )}
                    </TouchableOpacity>
                </View>

                <View style={styles.tabContainer}>
                    <TouchableOpacity
                        style={[styles.tab, activeTab === 'metrics' && styles.activeTab]}
                        onPress={() => setActiveTab('metrics')}
                    >
                        <Text style={[styles.tabText, activeTab === 'metrics' && styles.activeTabText]}>
                            Chỉ số
                        </Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[styles.tab, activeTab === 'medical' && styles.activeTab]}
                        onPress={() => setActiveTab('medical')}
                    >
                        <Text style={[styles.tabText, activeTab === 'medical' && styles.activeTabText]}>
                            Bệnh lý
                        </Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[styles.tab, activeTab === 'goals' && styles.activeTab]}
                        onPress={() => setActiveTab('goals')}
                    >
                        <Text style={[styles.tabText, activeTab === 'goals' && styles.activeTabText]}>
                            Mục tiêu
                        </Text>
                    </TouchableOpacity>
                </View>
            </LinearGradient>

            <ScrollView style={styles.content}>
                {activeTab === 'metrics' && renderMetricsTab()}
                {activeTab === 'medical' && renderMedicalTab()}
                {activeTab === 'goals' && renderGoalsTab()}
            </ScrollView>

            {/* Add Condition Modal */}
            <Modal
                visible={showConditionModal}
                animationType="slide"
                presentationStyle="pageSheet"
            >
                <View style={styles.modalContainer}>
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>Thêm tình trạng bệnh lý</Text>
                        <TouchableOpacity onPress={() => setShowConditionModal(false)}>
                            <Icon name="close" size={24} color={COLORS.textPrimary} />
                        </TouchableOpacity>
                    </View>

                    <View style={styles.modalContent}>
                        <TextInput
                            style={styles.modalInput}
                            value={newCondition}
                            onChangeText={setNewCondition}
                            placeholder="Nhập tên bệnh lý..."
                            autoFocus
                        />

                        <Text style={styles.suggestionsTitle}>Gợi ý:</Text>
                        <View style={styles.suggestionsContainer}>
                            {commonConditions.map((condition, index) => (
                                <TouchableOpacity
                                    key={index}
                                    style={styles.suggestionChip}
                                    onPress={() => setNewCondition(condition)}
                                >
                                    <Text style={styles.suggestionText}>{condition}</Text>
                                </TouchableOpacity>
                            ))}
                        </View>

                        <TouchableOpacity
                            style={[styles.addModalButton, { opacity: newCondition.trim() ? 1 : 0.5 }]}
                            onPress={addCondition}
                            disabled={!newCondition.trim()}
                        >
                            <Text style={styles.addModalButtonText}>Thêm</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>

            {/* Add Allergy Modal */}
            <Modal
                visible={showAllergyModal}
                animationType="slide"
                presentationStyle="pageSheet"
            >
                <View style={styles.modalContainer}>
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>Thêm dị ứng thực phẩm</Text>
                        <TouchableOpacity onPress={() => setShowAllergyModal(false)}>
                            <Icon name="close" size={24} color={COLORS.textPrimary} />
                        </TouchableOpacity>
                    </View>

                    <View style={styles.modalContent}>
                        <TextInput
                            style={styles.modalInput}
                            value={newAllergy}
                            onChangeText={setNewAllergy}
                            placeholder="Nhập tên thực phẩm dị ứng..."
                            autoFocus
                        />

                        <Text style={styles.suggestionsTitle}>Gợi ý:</Text>
                        <View style={styles.suggestionsContainer}>
                            {commonAllergies.map((allergy, index) => (
                                <TouchableOpacity
                                    key={index}
                                    style={styles.suggestionChip}
                                    onPress={() => setNewAllergy(allergy)}
                                >
                                    <Text style={styles.suggestionText}>{allergy}</Text>
                                </TouchableOpacity>
                            ))}
                        </View>

                        <TouchableOpacity
                            style={[styles.addModalButton, { opacity: newAllergy.trim() ? 1 : 0.5 }]}
                            onPress={addAllergy}
                            disabled={!newAllergy.trim()}
                        >
                            <Text style={styles.addModalButtonText}>Thêm</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>
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
        marginBottom: 20,
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
    editButton: {
        padding: 5,
    },
    tabContainer: {
        flexDirection: 'row',
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        borderRadius: 25,
        padding: 4,
    },
    tab: {
        flex: 1,
        paddingVertical: 10,
        alignItems: 'center',
        borderRadius: 20,
    },
    activeTab: {
        backgroundColor: COLORS.white,
    },
    tabText: {
        color: COLORS.white,
        fontSize: 14,
        fontWeight: '500',
    },
    activeTabText: {
        color: COLORS.primary,
    },
    content: {
        flex: 1,
    },
    tabContent: {
        padding: 20,
    },
    inputGroup: {
        marginBottom: 20,
    },
    inputLabel: {
        fontSize: 16,
        fontWeight: '500',
        color: COLORS.textPrimary,
        marginBottom: 8,
    },
    input: {
        borderWidth: 1,
        borderColor: COLORS.lightGray,
        borderRadius: 10,
        paddingHorizontal: 15,
        paddingVertical: 12,
        fontSize: 16,
        backgroundColor: COLORS.white,
    },
    disabledInput: {
        backgroundColor: COLORS.background,
        color: COLORS.textSecondary,
    },
    bmiCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 20,
        alignItems: 'center',
        marginTop: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    bmiTitle: {
        fontSize: 16,
        color: COLORS.textSecondary,
    },
    bmiValue: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginVertical: 8,
    },
    bmiStatus: {
        fontSize: 14,
        color: COLORS.textSecondary,
    },
    section: {
        marginBottom: 30,
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 15,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
    },
    addButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 15,
        width: 30,
        height: 30,
        justifyContent: 'center',
        alignItems: 'center',
    },
    chipContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    chip: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFEBEE',
        borderRadius: 20,
        paddingHorizontal: 12,
        paddingVertical: 8,
        margin: 4,
    },
    allergyChip: {
        backgroundColor: '#FFF3E0',
    },
    chipText: {
        color: COLORS.error,
        fontSize: 14,
        marginRight: 8,
    },
    allergyText: {
        color: COLORS.warning,
    },
    emptyText: {
        color: COLORS.textSecondary,
        fontStyle: 'italic',
        padding: 20,
        textAlign: 'center',
    },
    modalContainer: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    modalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 15,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.lightGray,
    },
    modalTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
    },
    modalContent: {
        flex: 1,
        padding: 20,
    },
    modalInput: {
        borderWidth: 1,
        borderColor: COLORS.lightGray,
        borderRadius: 10,
        paddingHorizontal: 15,
        paddingVertical: 12,
        fontSize: 16,
        backgroundColor: COLORS.white,
        marginBottom: 20,
    },
    suggestionsTitle: {
        fontSize: 16,
        fontWeight: '500',
        color: COLORS.textPrimary,
        marginBottom: 10,
    },
    suggestionsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 30,
    },
    suggestionChip: {
        backgroundColor: COLORS.primaryLighter,
        borderRadius: 20,
        paddingHorizontal: 12,
        paddingVertical: 8,
        margin: 4,
    },
    suggestionText: {
        color: COLORS.primary,
        fontSize: 14,
    },
    addModalButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 25,
        paddingVertical: 15,
        alignItems: 'center',
    },
    addModalButtonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default HealthInfoScreen;