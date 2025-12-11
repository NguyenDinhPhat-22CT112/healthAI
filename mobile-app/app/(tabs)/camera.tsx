import React, { useState, useRef } from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
    ScrollView,
    Modal,
    Dimensions,
} from 'react-native';
import { Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { PieChart } from 'react-native-chart-kit';
import { apiService } from '../../src/services/apiService';
import { useHealth } from '../../contexts/HealthContext';

const { width, height } = Dimensions.get('window');

const COLORS = {
    primary: '#2E7D32',
    primaryLight: '#4CAF50',
    white: '#FFFFFF',
    black: '#000000',
    textPrimary: '#212121',
    textSecondary: '#757575',
    warning: '#FF9800',
    background: '#F5F5F5',
};

export default function CameraScreen() {
    const [hasPermission, setHasPermission] = useState<boolean | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<any>(null);
    const [showResult, setShowResult] = useState(false);
    const cameraRef = useRef<Camera>(null);
    const { addFoodEntry } = useHealth();

    React.useEffect(() => {
        (async () => {
            const { status } = await Camera.requestCameraPermissionsAsync();
            setHasPermission(status === 'granted');
        })();
    }, []);

    const takePicture = async () => {
        if (cameraRef.current) {
            try {
                const photo = await cameraRef.current.takePictureAsync({
                    quality: 0.8,
                    base64: false,
                });
                analyzeFood(photo.uri);
            } catch (error) {
                Alert.alert('Lỗi', 'Không thể chụp ảnh');
            }
        }
    };

    const pickImage = async () => {
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
        });

        if (!result.canceled && result.assets[0]) {
            analyzeFood(result.assets[0].uri);
        }
    };

    const analyzeFood = async (imageUri: string) => {
        setIsAnalyzing(true);
        try {
            const response = await apiService.analyzeFood(imageUri);

            if (response.success && response.data) {
                setAnalysisResult(response.data);
                setShowResult(true);
            } else {
                Alert.alert('Lỗi', response.error || 'Không thể phân tích món ăn');
            }
        } catch (error) {
            Alert.alert('Lỗi', 'Có lỗi xảy ra khi phân tích món ăn');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const saveToHistory = async () => {
        if (analysisResult) {
            const success = await addFoodEntry({
                ...analysisResult,
                timestamp: new Date().toISOString(),
            });

            if (success) {
                Alert.alert('Thành công', 'Đã lưu vào lịch sử ăn uống');
                setShowResult(false);
                setAnalysisResult(null);
            } else {
                Alert.alert('Lỗi', 'Không thể lưu vào lịch sử');
            }
        }
    };

    if (hasPermission === null) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    if (hasPermission === false) {
        return (
            <View style={styles.container}>
                <Text style={styles.noPermissionText}>
                    Cần quyền truy cập camera để sử dụng tính năng này
                </Text>
                <TouchableOpacity
                    style={styles.permissionButton}
                    onPress={() => Camera.requestCameraPermissionsAsync()}
                >
                    <Text style={styles.permissionButtonText}>Cấp quyền</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const nutritionData = analysisResult ? [
        {
            name: 'Protein',
            population: analysisResult.protein || 0,
            color: '#2196F3',
            legendFontColor: COLORS.textPrimary,
            legendFontSize: 12,
        },
        {
            name: 'Carbs',
            population: analysisResult.carbs || 0,
            color: '#FF9800',
            legendFontColor: COLORS.textPrimary,
            legendFontSize: 12,
        },
        {
            name: 'Fat',
            population: analysisResult.fat || 0,
            color: '#F44336',
            legendFontColor: COLORS.textPrimary,
            legendFontSize: 12,
        },
    ] : [];

    return (
        <View style={styles.container}>
            {isAnalyzing && (
                <View style={styles.loadingOverlay}>
                    <ActivityIndicator size="large" color={COLORS.white} />
                    <Text style={styles.loadingText}>Đang phân tích món ăn...</Text>
                </View>
            )}

            <Camera style={styles.camera} ref={cameraRef}>
                <View style={styles.cameraOverlay}>
                    <View style={styles.scanFrame} />
                    <Text style={styles.instructionText}>
                        Đặt món ăn vào khung hình và chụp ảnh
                    </Text>
                </View>
            </Camera>

            <View style={styles.controls}>
                <TouchableOpacity style={styles.galleryButton} onPress={pickImage}>
                    <MaterialIcons name="photo-library" size={24} color={COLORS.white} />
                </TouchableOpacity>

                <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                    <View style={styles.captureButtonInner} />
                </TouchableOpacity>

                <TouchableOpacity style={styles.flashButton}>
                    <MaterialIcons name="flash-off" size={24} color={COLORS.white} />
                </TouchableOpacity>
            </View>

            {/* Analysis Result Modal */}
            <Modal
                visible={showResult}
                animationType="slide"
                presentationStyle="pageSheet"
            >
                <View style={styles.modalContainer}>
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>Kết quả phân tích</Text>
                        <TouchableOpacity
                            style={styles.closeButton}
                            onPress={() => setShowResult(false)}
                        >
                            <MaterialIcons name="close" size={24} color={COLORS.textPrimary} />
                        </TouchableOpacity>
                    </View>

                    <ScrollView style={styles.modalContent}>
                        {analysisResult && (
                            <>
                                <View style={styles.foodInfo}>
                                    <Text style={styles.foodName}>{analysisResult.foodName}</Text>
                                    <Text style={styles.confidence}>
                                        Độ tin cậy: {Math.round((analysisResult.confidence || 0) * 100)}%
                                    </Text>
                                </View>

                                <View style={styles.caloriesSection}>
                                    <LinearGradient
                                        colors={[COLORS.primary, COLORS.primaryLight]}
                                        style={styles.caloriesCard}
                                    >
                                        <Text style={styles.caloriesValue}>
                                            {analysisResult.calories || 0}
                                        </Text>
                                        <Text style={styles.caloriesLabel}>Calories</Text>
                                    </LinearGradient>
                                </View>

                                <View style={styles.nutritionSection}>
                                    <Text style={styles.sectionTitle}>Thành phần dinh dưỡng</Text>

                                    <View style={styles.nutritionGrid}>
                                        <View style={styles.nutritionItem}>
                                            <Text style={styles.nutritionValue}>
                                                {analysisResult.protein || 0}g
                                            </Text>
                                            <Text style={styles.nutritionLabel}>Protein</Text>
                                        </View>

                                        <View style={styles.nutritionItem}>
                                            <Text style={styles.nutritionValue}>
                                                {analysisResult.carbs || 0}g
                                            </Text>
                                            <Text style={styles.nutritionLabel}>Carbs</Text>
                                        </View>

                                        <View style={styles.nutritionItem}>
                                            <Text style={styles.nutritionValue}>
                                                {analysisResult.fat || 0}g
                                            </Text>
                                            <Text style={styles.nutritionLabel}>Fat</Text>
                                        </View>

                                        <View style={styles.nutritionItem}>
                                            <Text style={styles.nutritionValue}>
                                                {analysisResult.fiber || 0}g
                                            </Text>
                                            <Text style={styles.nutritionLabel}>Fiber</Text>
                                        </View>
                                    </View>

                                    {nutritionData.length > 0 && (
                                        <View style={styles.chartContainer}>
                                            <PieChart
                                                data={nutritionData}
                                                width={width - 40}
                                                height={200}
                                                chartConfig={{
                                                    color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                                                }}
                                                accessor="population"
                                                backgroundColor="transparent"
                                                paddingLeft="15"
                                                absolute
                                            />
                                        </View>
                                    )}
                                </View>

                                {analysisResult.healthAdvice && (
                                    <View style={styles.adviceSection}>
                                        <Text style={styles.sectionTitle}>Lời khuyên sức khỏe</Text>
                                        <View style={styles.adviceCard}>
                                            <MaterialIcons name="lightbulb" size={24} color={COLORS.warning} />
                                            <Text style={styles.adviceText}>
                                                {analysisResult.healthAdvice}
                                            </Text>
                                        </View>
                                    </View>
                                )}

                                <View style={styles.actionButtons}>
                                    <TouchableOpacity
                                        style={styles.saveButton}
                                        onPress={saveToHistory}
                                    >
                                        <MaterialIcons name="save" size={20} color={COLORS.white} />
                                        <Text style={styles.saveButtonText}>Lưu vào lịch sử</Text>
                                    </TouchableOpacity>

                                    <TouchableOpacity
                                        style={styles.shareButton}
                                        onPress={() => {/* Implement share functionality */ }}
                                    >
                                        <MaterialIcons name="share" size={20} color={COLORS.primary} />
                                        <Text style={styles.shareButtonText}>Chia sẻ</Text>
                                    </TouchableOpacity>
                                </View>
                            </>
                        )}
                    </ScrollView>
                </View>
            </Modal>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.black,
    },
    camera: {
        flex: 1,
    },
    cameraOverlay: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    scanFrame: {
        width: 250,
        height: 250,
        borderWidth: 2,
        borderColor: COLORS.white,
        borderRadius: 20,
        backgroundColor: 'transparent',
    },
    instructionText: {
        color: COLORS.white,
        fontSize: 16,
        textAlign: 'center',
        marginTop: 20,
        paddingHorizontal: 40,
    },
    controls: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 40,
        paddingVertical: 30,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
    },
    galleryButton: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: 'rgba(255, 255, 255, 0.3)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    captureButton: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: COLORS.white,
        justifyContent: 'center',
        alignItems: 'center',
    },
    captureButtonInner: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: COLORS.primary,
    },
    flashButton: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: 'rgba(255, 255, 255, 0.3)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingOverlay: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
    },
    loadingText: {
        color: COLORS.white,
        fontSize: 16,
        marginTop: 20,
    },
    noPermissionText: {
        fontSize: 18,
        textAlign: 'center',
        color: COLORS.textPrimary,
        marginBottom: 20,
    },
    permissionButton: {
        backgroundColor: COLORS.primary,
        paddingHorizontal: 30,
        paddingVertical: 15,
        borderRadius: 25,
    },
    permissionButtonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
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
        borderBottomColor: '#E0E0E0',
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
    },
    closeButton: {
        padding: 5,
    },
    modalContent: {
        flex: 1,
        padding: 20,
    },
    foodInfo: {
        alignItems: 'center',
        marginBottom: 20,
    },
    foodName: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        textAlign: 'center',
    },
    confidence: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 5,
    },
    caloriesSection: {
        alignItems: 'center',
        marginBottom: 30,
    },
    caloriesCard: {
        paddingHorizontal: 40,
        paddingVertical: 20,
        borderRadius: 20,
        alignItems: 'center',
    },
    caloriesValue: {
        fontSize: 48,
        fontWeight: 'bold',
        color: COLORS.white,
    },
    caloriesLabel: {
        fontSize: 16,
        color: COLORS.white,
        opacity: 0.9,
    },
    nutritionSection: {
        marginBottom: 30,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 15,
    },
    nutritionGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        marginBottom: 20,
    },
    nutritionItem: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        alignItems: 'center',
        width: (width - 60) / 2,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    nutritionValue: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    nutritionLabel: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 5,
    },
    chartContainer: {
        alignItems: 'center',
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    adviceSection: {
        marginBottom: 30,
    },
    adviceCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        flexDirection: 'row',
        alignItems: 'flex-start',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    adviceText: {
        flex: 1,
        fontSize: 14,
        color: COLORS.textPrimary,
        marginLeft: 15,
        lineHeight: 20,
    },
    actionButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 20,
    },
    saveButton: {
        backgroundColor: COLORS.primary,
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 15,
        borderRadius: 25,
        flex: 0.48,
        justifyContent: 'center',
    },
    saveButtonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
        marginLeft: 8,
    },
    shareButton: {
        backgroundColor: COLORS.white,
        borderWidth: 2,
        borderColor: COLORS.primary,
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 15,
        borderRadius: 25,
        flex: 0.48,
        justifyContent: 'center',
    },
    shareButtonText: {
        color: COLORS.primary,
        fontSize: 16,
        fontWeight: 'bold',
        marginLeft: 8,
    },
});