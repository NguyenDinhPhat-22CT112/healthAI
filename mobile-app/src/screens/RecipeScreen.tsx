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
    Dimensions,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../services/apiService';
import { useHealth } from '../contexts/HealthContext';
import { COLORS } from '../constants/colors';

const { width } = Dimensions.get('window');

interface Recipe {
    id: string;
    name: string;
    ingredients: string[];
    instructions: string[];
    cookingTime: number;
    servings: number;
    difficulty: 'Dễ' | 'Trung bình' | 'Khó';
    nutrition: {
        calories: number;
        protein: number;
        carbs: number;
        fat: number;
    };
    healthBenefits: string[];
    warnings?: string[];
}

const RecipeScreen = () => {
    const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate');
    const [ingredients, setIngredients] = useState<string[]>([]);
    const [newIngredient, setNewIngredient] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [generatedRecipe, setGeneratedRecipe] = useState<Recipe | null>(null);
    const [showRecipeModal, setShowRecipeModal] = useState(false);
    const [savedRecipes, setSavedRecipes] = useState<Recipe[]>([]);
    const { medicalHistory } = useHealth();

    useEffect(() => {
        loadSavedRecipes();
    }, []);

    const loadSavedRecipes = async () => {
        // Load saved recipes from local storage or API
        // This is a placeholder implementation
        setSavedRecipes([]);
    };

    const addIngredient = () => {
        if (newIngredient.trim() && !ingredients.includes(newIngredient.trim())) {
            setIngredients([...ingredients, newIngredient.trim()]);
            setNewIngredient('');
        }
    };

    const removeIngredient = (ingredient: string) => {
        setIngredients(ingredients.filter(item => item !== ingredient));
    };

    const analyzeIngredientsFromImage = async () => {
        try {
            const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
                allowsEditing: true,
                aspect: [4, 3],
                quality: 0.8,
            });

            if (!result.canceled && result.assets[0]) {
                setIsAnalyzing(true);
                const response = await apiService.analyzeIngredients(result.assets[0].uri);

                if (response.success && response.data) {
                    const detectedIngredients = response.data.ingredients || [];
                    setIngredients([...new Set([...ingredients, ...detectedIngredients])]);
                } else {
                    Alert.alert('Lỗi', 'Không thể phân tích nguyên liệu từ hình ảnh');
                }
            }
        } catch (error) {
            Alert.alert('Lỗi', 'Có lỗi xảy ra khi phân tích hình ảnh');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const generateRecipe = async () => {
        if (ingredients.length === 0) {
            Alert.alert('Thông báo', 'Vui lòng thêm ít nhất một nguyên liệu');
            return;
        }

        setIsGenerating(true);
        try {
            const preferences = {
                medicalConditions: medicalHistory?.conditions || [],
                allergies: medicalHistory?.allergies || [],
                dietaryRestrictions: medicalHistory?.dietaryRestrictions || [],
            };

            const response = await apiService.generateRecipe(ingredients, preferences);

            if (response.success && response.data) {
                setGeneratedRecipe(response.data);
                setShowRecipeModal(true);
            } else {
                Alert.alert('Lỗi', response.error || 'Không thể tạo công thức');
            }
        } catch (error) {
            Alert.alert('Lỗi', 'Có lỗi xảy ra khi tạo công thức');
        } finally {
            setIsGenerating(false);
        }
    };

    const saveRecipe = () => {
        if (generatedRecipe) {
            setSavedRecipes([generatedRecipe, ...savedRecipes]);
            Alert.alert('Thành công', 'Đã lưu công thức');
            setShowRecipeModal(false);
        }
    };

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'Dễ': return COLORS.success;
            case 'Trung bình': return COLORS.warning;
            case 'Khó': return COLORS.error;
            default: return COLORS.gray;
        }
    };

    const renderIngredientsList = () => (
        <View style={styles.ingredientsSection}>
            <Text style={styles.sectionTitle}>Nguyên liệu có sẵn</Text>

            <View style={styles.addIngredientContainer}>
                <TextInput
                    style={styles.ingredientInput}
                    value={newIngredient}
                    onChangeText={setNewIngredient}
                    placeholder="Thêm nguyên liệu..."
                    placeholderTextColor={COLORS.gray}
                    onSubmitEditing={addIngredient}
                />
                <TouchableOpacity style={styles.addButton} onPress={addIngredient}>
                    <Icon name="add" size={24} color={COLORS.white} />
                </TouchableOpacity>
            </View>

            <TouchableOpacity
                style={styles.cameraButton}
                onPress={analyzeIngredientsFromImage}
                disabled={isAnalyzing}
            >
                {isAnalyzing ? (
                    <ActivityIndicator color={COLORS.primary} />
                ) : (
                    <Icon name="camera-alt" size={20} color={COLORS.primary} />
                )}
                <Text style={styles.cameraButtonText}>
                    {isAnalyzing ? 'Đang phân tích...' : 'Chụp ảnh nguyên liệu'}
                </Text>
            </TouchableOpacity>

            <View style={styles.ingredientsList}>
                {ingredients.map((ingredient, index) => (
                    <View key={index} style={styles.ingredientChip}>
                        <Text style={styles.ingredientText}>{ingredient}</Text>
                        <TouchableOpacity onPress={() => removeIngredient(ingredient)}>
                            <Icon name="close" size={16} color={COLORS.gray} />
                        </TouchableOpacity>
                    </View>
                ))}
            </View>

            <TouchableOpacity
                style={[styles.generateButton, { opacity: ingredients.length > 0 ? 1 : 0.5 }]}
                onPress={generateRecipe}
                disabled={ingredients.length === 0 || isGenerating}
            >
                {isGenerating ? (
                    <ActivityIndicator color={COLORS.white} />
                ) : (
                    <>
                        <Icon name="restaurant" size={20} color={COLORS.white} />
                        <Text style={styles.generateButtonText}>Tạo công thức</Text>
                    </>
                )}
            </TouchableOpacity>
        </View>
    );

    const renderSavedRecipes = () => (
        <View style={styles.savedRecipesSection}>
            <Text style={styles.sectionTitle}>Công thức đã lưu</Text>

            {savedRecipes.length === 0 ? (
                <View style={styles.emptyState}>
                    <Icon name="restaurant-menu" size={64} color={COLORS.gray} />
                    <Text style={styles.emptyStateText}>Chưa có công thức nào được lưu</Text>
                    <Text style={styles.emptyStateSubtext}>
                        Tạo công thức mới để bắt đầu
                    </Text>
                </View>
            ) : (
                <ScrollView showsVerticalScrollIndicator={false}>
                    {savedRecipes.map((recipe, index) => (
                        <TouchableOpacity
                            key={index}
                            style={styles.recipeCard}
                            onPress={() => {
                                setGeneratedRecipe(recipe);
                                setShowRecipeModal(true);
                            }}
                        >
                            <View style={styles.recipeHeader}>
                                <Text style={styles.recipeName}>{recipe.name}</Text>
                                <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(recipe.difficulty) }]}>
                                    <Text style={styles.difficultyText}>{recipe.difficulty}</Text>
                                </View>
                            </View>

                            <View style={styles.recipeInfo}>
                                <View style={styles.recipeInfoItem}>
                                    <Icon name="schedule" size={16} color={COLORS.gray} />
                                    <Text style={styles.recipeInfoText}>{recipe.cookingTime} phút</Text>
                                </View>
                                <View style={styles.recipeInfoItem}>
                                    <Icon name="people" size={16} color={COLORS.gray} />
                                    <Text style={styles.recipeInfoText}>{recipe.servings} người</Text>
                                </View>
                                <View style={styles.recipeInfoItem}>
                                    <Icon name="local-fire-department" size={16} color={COLORS.gray} />
                                    <Text style={styles.recipeInfoText}>{recipe.nutrition.calories} kcal</Text>
                                </View>
                            </View>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            )}
        </View>
    );

    const renderRecipeModal = () => (
        <Modal
            visible={showRecipeModal}
            animationType="slide"
            presentationStyle="pageSheet"
        >
            <View style={styles.modalContainer}>
                <View style={styles.modalHeader}>
                    <Text style={styles.modalTitle}>{generatedRecipe?.name}</Text>
                    <TouchableOpacity
                        style={styles.closeButton}
                        onPress={() => setShowRecipeModal(false)}
                    >
                        <Icon name="close" size={24} color={COLORS.textPrimary} />
                    </TouchableOpacity>
                </View>

                <ScrollView style={styles.modalContent}>
                    {generatedRecipe && (
                        <>
                            <View style={styles.recipeOverview}>
                                <View style={styles.overviewItem}>
                                    <Icon name="schedule" size={20} color={COLORS.primary} />
                                    <Text style={styles.overviewText}>{generatedRecipe.cookingTime} phút</Text>
                                </View>
                                <View style={styles.overviewItem}>
                                    <Icon name="people" size={20} color={COLORS.primary} />
                                    <Text style={styles.overviewText}>{generatedRecipe.servings} người</Text>
                                </View>
                                <View style={styles.overviewItem}>
                                    <Icon name="star" size={20} color={getDifficultyColor(generatedRecipe.difficulty)} />
                                    <Text style={styles.overviewText}>{generatedRecipe.difficulty}</Text>
                                </View>
                            </View>

                            <View style={styles.nutritionOverview}>
                                <Text style={styles.subsectionTitle}>Thông tin dinh dưỡng</Text>
                                <View style={styles.nutritionGrid}>
                                    <View style={styles.nutritionItem}>
                                        <Text style={styles.nutritionValue}>{generatedRecipe.nutrition.calories}</Text>
                                        <Text style={styles.nutritionLabel}>Calories</Text>
                                    </View>
                                    <View style={styles.nutritionItem}>
                                        <Text style={styles.nutritionValue}>{generatedRecipe.nutrition.protein}g</Text>
                                        <Text style={styles.nutritionLabel}>Protein</Text>
                                    </View>
                                    <View style={styles.nutritionItem}>
                                        <Text style={styles.nutritionValue}>{generatedRecipe.nutrition.carbs}g</Text>
                                        <Text style={styles.nutritionLabel}>Carbs</Text>
                                    </View>
                                    <View style={styles.nutritionItem}>
                                        <Text style={styles.nutritionValue}>{generatedRecipe.nutrition.fat}g</Text>
                                        <Text style={styles.nutritionLabel}>Fat</Text>
                                    </View>
                                </View>
                            </View>

                            <View style={styles.section}>
                                <Text style={styles.subsectionTitle}>Nguyên liệu</Text>
                                {generatedRecipe.ingredients.map((ingredient, index) => (
                                    <View key={index} style={styles.ingredientItem}>
                                        <Icon name="fiber-manual-record" size={8} color={COLORS.primary} />
                                        <Text style={styles.ingredientItemText}>{ingredient}</Text>
                                    </View>
                                ))}
                            </View>

                            <View style={styles.section}>
                                <Text style={styles.subsectionTitle}>Cách làm</Text>
                                {generatedRecipe.instructions.map((instruction, index) => (
                                    <View key={index} style={styles.instructionItem}>
                                        <View style={styles.stepNumber}>
                                            <Text style={styles.stepNumberText}>{index + 1}</Text>
                                        </View>
                                        <Text style={styles.instructionText}>{instruction}</Text>
                                    </View>
                                ))}
                            </View>

                            {generatedRecipe.healthBenefits.length > 0 && (
                                <View style={styles.section}>
                                    <Text style={styles.subsectionTitle}>Lợi ích sức khỏe</Text>
                                    {generatedRecipe.healthBenefits.map((benefit, index) => (
                                        <View key={index} style={styles.benefitItem}>
                                            <Icon name="favorite" size={16} color={COLORS.success} />
                                            <Text style={styles.benefitText}>{benefit}</Text>
                                        </View>
                                    ))}
                                </View>
                            )}

                            {generatedRecipe.warnings && generatedRecipe.warnings.length > 0 && (
                                <View style={styles.section}>
                                    <Text style={styles.subsectionTitle}>Lưu ý</Text>
                                    {generatedRecipe.warnings.map((warning, index) => (
                                        <View key={index} style={styles.warningItem}>
                                            <Icon name="warning" size={16} color={COLORS.warning} />
                                            <Text style={styles.warningText}>{warning}</Text>
                                        </View>
                                    ))}
                                </View>
                            )}

                            <View style={styles.actionButtons}>
                                <TouchableOpacity style={styles.saveButton} onPress={saveRecipe}>
                                    <Icon name="bookmark" size={20} color={COLORS.white} />
                                    <Text style={styles.saveButtonText}>Lưu công thức</Text>
                                </TouchableOpacity>

                                <TouchableOpacity style={styles.shareButton}>
                                    <Icon name="share" size={20} color={COLORS.primary} />
                                    <Text style={styles.shareButtonText}>Chia sẻ</Text>
                                </TouchableOpacity>
                            </View>
                        </>
                    )}
                </ScrollView>
            </View>
        </Modal>
    );

    return (
        <View style={styles.container}>
            <LinearGradient
                colors={[COLORS.gradientStart, COLORS.gradientEnd]}
                style={styles.header}
            >
                <Text style={styles.headerTitle}>Công thức nấu ăn</Text>
                <View style={styles.tabContainer}>
                    <TouchableOpacity
                        style={[styles.tab, activeTab === 'generate' && styles.activeTab]}
                        onPress={() => setActiveTab('generate')}
                    >
                        <Text style={[styles.tabText, activeTab === 'generate' && styles.activeTabText]}>
                            Tạo mới
                        </Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[styles.tab, activeTab === 'history' && styles.activeTab]}
                        onPress={() => setActiveTab('history')}
                    >
                        <Text style={[styles.tabText, activeTab === 'history' && styles.activeTabText]}>
                            Đã lưu
                        </Text>
                    </TouchableOpacity>
                </View>
            </LinearGradient>

            <ScrollView style={styles.content}>
                {activeTab === 'generate' ? renderIngredientsList() : renderSavedRecipes()}
            </ScrollView>

            {renderRecipeModal()}
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
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.white,
        textAlign: 'center',
        marginBottom: 20,
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
        fontSize: 16,
        fontWeight: '500',
    },
    activeTabText: {
        color: COLORS.primary,
    },
    content: {
        flex: 1,
        padding: 20,
    },
    ingredientsSection: {
        flex: 1,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 20,
    },
    addIngredientContainer: {
        flexDirection: 'row',
        marginBottom: 15,
    },
    ingredientInput: {
        flex: 1,
        borderWidth: 1,
        borderColor: COLORS.lightGray,
        borderRadius: 25,
        paddingHorizontal: 15,
        paddingVertical: 12,
        fontSize: 16,
        marginRight: 10,
    },
    addButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 25,
        width: 48,
        height: 48,
        justifyContent: 'center',
        alignItems: 'center',
    },
    cameraButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: COLORS.white,
        borderWidth: 2,
        borderColor: COLORS.primary,
        borderStyle: 'dashed',
        borderRadius: 15,
        paddingVertical: 15,
        marginBottom: 20,
    },
    cameraButtonText: {
        color: COLORS.primary,
        fontSize: 16,
        fontWeight: '500',
        marginLeft: 8,
    },
    ingredientsList: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 30,
    },
    ingredientChip: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.primaryLighter,
        borderRadius: 20,
        paddingHorizontal: 12,
        paddingVertical: 8,
        margin: 4,
    },
    ingredientText: {
        color: COLORS.primary,
        fontSize: 14,
        marginRight: 8,
    },
    generateButton: {
        backgroundColor: COLORS.primary,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 25,
        paddingVertical: 15,
    },
    generateButtonText: {
        color: COLORS.white,
        fontSize: 18,
        fontWeight: 'bold',
        marginLeft: 8,
    },
    savedRecipesSection: {
        flex: 1,
    },
    emptyState: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 60,
    },
    emptyStateText: {
        fontSize: 18,
        color: COLORS.textSecondary,
        marginTop: 20,
        textAlign: 'center',
    },
    emptyStateSubtext: {
        fontSize: 14,
        color: COLORS.gray,
        marginTop: 8,
        textAlign: 'center',
    },
    recipeCard: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        marginBottom: 15,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    recipeHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    recipeName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        flex: 1,
    },
    difficultyBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    difficultyText: {
        color: COLORS.white,
        fontSize: 12,
        fontWeight: 'bold',
    },
    recipeInfo: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    recipeInfoItem: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    recipeInfoText: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginLeft: 4,
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
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        flex: 1,
    },
    closeButton: {
        padding: 5,
    },
    modalContent: {
        flex: 1,
        padding: 20,
    },
    recipeOverview: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        backgroundColor: COLORS.white,
        borderRadius: 15,
        paddingVertical: 20,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    overviewItem: {
        alignItems: 'center',
    },
    overviewText: {
        fontSize: 14,
        color: COLORS.textPrimary,
        marginTop: 5,
        fontWeight: '500',
    },
    nutritionOverview: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    subsectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 15,
    },
    nutritionGrid: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    nutritionItem: {
        alignItems: 'center',
        flex: 1,
    },
    nutritionValue: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    nutritionLabel: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: 4,
    },
    section: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    ingredientItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    ingredientItemText: {
        fontSize: 16,
        color: COLORS.textPrimary,
        marginLeft: 10,
    },
    instructionItem: {
        flexDirection: 'row',
        marginBottom: 15,
    },
    stepNumber: {
        width: 24,
        height: 24,
        borderRadius: 12,
        backgroundColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 12,
        marginTop: 2,
    },
    stepNumberText: {
        color: COLORS.white,
        fontSize: 12,
        fontWeight: 'bold',
    },
    instructionText: {
        flex: 1,
        fontSize: 16,
        color: COLORS.textPrimary,
        lineHeight: 24,
    },
    benefitItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    benefitText: {
        fontSize: 14,
        color: COLORS.textPrimary,
        marginLeft: 8,
        flex: 1,
    },
    warningItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    warningText: {
        fontSize: 14,
        color: COLORS.textPrimary,
        marginLeft: 8,
        flex: 1,
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

export default RecipeScreen;