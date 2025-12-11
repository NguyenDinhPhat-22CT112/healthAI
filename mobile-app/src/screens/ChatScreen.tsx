import React, { useState, useRef, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    FlatList,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { useHealth } from '../contexts/HealthContext';
import { COLORS } from '../constants/colors';

interface Message {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
    type?: 'text' | 'suggestion' | 'warning';
}

const ChatScreen = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const flatListRef = useRef<FlatList>(null);
    const { user } = useAuth();
    const { medicalHistory, healthMetrics } = useHealth();

    useEffect(() => {
        // Welcome message
        const welcomeMessage: Message = {
            id: '1',
            text: `Xin chào ${user?.name || 'bạn'}! Tôi là trợ lý dinh dưỡng AI. Tôi có thể giúp bạn tư vấn về chế độ ăn uống phù hợp với tình trạng sức khỏe của bạn. Bạn có câu hỏi gì không?`,
            isUser: false,
            timestamp: new Date(),
            type: 'text',
        };
        setMessages([welcomeMessage]);
    }, [user]);

    const sendMessage = async () => {
        if (!inputText.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputText.trim(),
            isUser: true,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsLoading(true);

        try {
            // Prepare context for AI
            const context = {
                medicalConditions: medicalHistory?.conditions || [],
                allergies: medicalHistory?.allergies || [],
                medications: medicalHistory?.medications || [],
                healthMetrics: healthMetrics,
                userProfile: {
                    name: user?.name,
                    email: user?.email,
                },
            };

            const response = await apiService.sendChatMessage(userMessage.text, context);

            if (response.success && response.data) {
                const aiMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    text: response.data.message,
                    isUser: false,
                    timestamp: new Date(),
                    type: response.data.type || 'text',
                };

                setMessages(prev => [...prev, aiMessage]);

                // Add suggestions if provided
                if (response.data.suggestions && response.data.suggestions.length > 0) {
                    response.data.suggestions.forEach((suggestion: string, index: number) => {
                        const suggestionMessage: Message = {
                            id: (Date.now() + index + 2).toString(),
                            text: suggestion,
                            isUser: false,
                            timestamp: new Date(),
                            type: 'suggestion',
                        };
                        setMessages(prev => [...prev, suggestionMessage]);
                    });
                }
            } else {
                throw new Error(response.error || 'Có lỗi xảy ra');
            }
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau.',
                isUser: false,
                timestamp: new Date(),
                type: 'text',
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionPress = (suggestion: string) => {
        setInputText(suggestion);
    };

    const renderMessage = ({ item }: { item: Message }) => {
        const isUser = item.isUser;
        const messageStyle = isUser ? styles.userMessage : styles.aiMessage;
        const containerStyle = isUser ? styles.userMessageContainer : styles.aiMessageContainer;

        if (item.type === 'suggestion') {
            return (
                <TouchableOpacity
                    style={styles.suggestionContainer}
                    onPress={() => handleSuggestionPress(item.text)}
                >
                    <Icon name="lightbulb-outline" size={16} color={COLORS.primary} />
                    <Text style={styles.suggestionText}>{item.text}</Text>
                </TouchableOpacity>
            );
        }

        if (item.type === 'warning') {
            return (
                <View style={styles.warningContainer}>
                    <Icon name="warning" size={20} color={COLORS.warning} />
                    <Text style={styles.warningText}>{item.text}</Text>
                </View>
            );
        }

        return (
            <View style={containerStyle}>
                {!isUser && (
                    <View style={styles.aiAvatar}>
                        <Icon name="smart-toy" size={20} color={COLORS.white} />
                    </View>
                )}
                <View style={messageStyle}>
                    <Text style={isUser ? styles.userMessageText : styles.aiMessageText}>
                        {item.text}
                    </Text>
                    <Text style={styles.messageTime}>
                        {item.timestamp.toLocaleTimeString('vi-VN', {
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                    </Text>
                </View>
            </View>
        );
    };

    const quickQuestions = [
        'Tôi bị tiểu đường, nên ăn gì?',
        'Thực đơn cho người cao huyết áp',
        'Cách giảm cân an toàn',
        'Thực phẩm tốt cho tim mạch',
        'Chế độ ăn cho người bệnh thận',
    ];

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <LinearGradient
                colors={[COLORS.gradientStart, COLORS.gradientEnd]}
                style={styles.header}
            >
                <View style={styles.headerContent}>
                    <Icon name="smart-toy" size={24} color={COLORS.white} />
                    <Text style={styles.headerTitle}>Tư vấn dinh dưỡng AI</Text>
                    <TouchableOpacity style={styles.infoButton}>
                        <Icon name="info-outline" size={24} color={COLORS.white} />
                    </TouchableOpacity>
                </View>
            </LinearGradient>

            <FlatList
                ref={flatListRef}
                data={messages}
                renderItem={renderMessage}
                keyExtractor={(item) => item.id}
                style={styles.messagesList}
                contentContainerStyle={styles.messagesContainer}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
                showsVerticalScrollIndicator={false}
            />

            {messages.length === 1 && (
                <View style={styles.quickQuestionsContainer}>
                    <Text style={styles.quickQuestionsTitle}>Câu hỏi gợi ý:</Text>
                    {quickQuestions.map((question, index) => (
                        <TouchableOpacity
                            key={index}
                            style={styles.quickQuestionButton}
                            onPress={() => setInputText(question)}
                        >
                            <Text style={styles.quickQuestionText}>{question}</Text>
                        </TouchableOpacity>
                    ))}
                </View>
            )}

            {isLoading && (
                <View style={styles.typingIndicator}>
                    <View style={styles.aiAvatar}>
                        <Icon name="smart-toy" size={16} color={COLORS.white} />
                    </View>
                    <View style={styles.typingBubble}>
                        <ActivityIndicator size="small" color={COLORS.primary} />
                        <Text style={styles.typingText}>Đang suy nghĩ...</Text>
                    </View>
                </View>
            )}

            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.textInput}
                    value={inputText}
                    onChangeText={setInputText}
                    placeholder="Nhập câu hỏi của bạn..."
                    placeholderTextColor={COLORS.gray}
                    multiline
                    maxLength={500}
                />
                <TouchableOpacity
                    style={[styles.sendButton, { opacity: inputText.trim() ? 1 : 0.5 }]}
                    onPress={sendMessage}
                    disabled={!inputText.trim() || isLoading}
                >
                    <Icon name="send" size={24} color={COLORS.white} />
                </TouchableOpacity>
            </View>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        paddingTop: 10,
        paddingBottom: 15,
        paddingHorizontal: 20,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    headerTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.white,
        flex: 1,
        textAlign: 'center',
    },
    infoButton: {
        padding: 5,
    },
    messagesList: {
        flex: 1,
    },
    messagesContainer: {
        padding: 20,
        paddingBottom: 10,
    },
    userMessageContainer: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        marginBottom: 15,
    },
    aiMessageContainer: {
        flexDirection: 'row',
        justifyContent: 'flex-start',
        marginBottom: 15,
    },
    userMessage: {
        backgroundColor: COLORS.primary,
        borderRadius: 20,
        borderBottomRightRadius: 5,
        paddingHorizontal: 15,
        paddingVertical: 10,
        maxWidth: '80%',
    },
    aiMessage: {
        backgroundColor: COLORS.white,
        borderRadius: 20,
        borderBottomLeftRadius: 5,
        paddingHorizontal: 15,
        paddingVertical: 10,
        maxWidth: '80%',
        marginLeft: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    aiAvatar: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        alignSelf: 'flex-end',
    },
    userMessageText: {
        color: COLORS.white,
        fontSize: 16,
        lineHeight: 22,
    },
    aiMessageText: {
        color: COLORS.textPrimary,
        fontSize: 16,
        lineHeight: 22,
    },
    messageTime: {
        fontSize: 12,
        color: COLORS.gray,
        marginTop: 5,
        alignSelf: 'flex-end',
    },
    suggestionContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.primaryLighter,
        borderRadius: 15,
        paddingHorizontal: 12,
        paddingVertical: 8,
        marginBottom: 10,
        marginLeft: 42,
        maxWidth: '80%',
    },
    suggestionText: {
        color: COLORS.primary,
        fontSize: 14,
        marginLeft: 8,
        fontWeight: '500',
    },
    warningContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFF3CD',
        borderRadius: 15,
        paddingHorizontal: 12,
        paddingVertical: 10,
        marginBottom: 10,
        marginLeft: 42,
        maxWidth: '80%',
        borderLeftWidth: 4,
        borderLeftColor: COLORS.warning,
    },
    warningText: {
        color: '#856404',
        fontSize: 14,
        marginLeft: 8,
        flex: 1,
    },
    quickQuestionsContainer: {
        padding: 20,
        backgroundColor: COLORS.white,
        borderTopWidth: 1,
        borderTopColor: COLORS.lightGray,
    },
    quickQuestionsTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.textPrimary,
        marginBottom: 10,
    },
    quickQuestionButton: {
        backgroundColor: COLORS.primaryLighter,
        borderRadius: 20,
        paddingHorizontal: 15,
        paddingVertical: 10,
        marginBottom: 8,
    },
    quickQuestionText: {
        color: COLORS.primary,
        fontSize: 14,
        fontWeight: '500',
    },
    typingIndicator: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 10,
    },
    typingBubble: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.white,
        borderRadius: 20,
        paddingHorizontal: 15,
        paddingVertical: 10,
        marginLeft: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    typingText: {
        color: COLORS.textSecondary,
        fontSize: 14,
        marginLeft: 8,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        paddingHorizontal: 20,
        paddingVertical: 15,
        backgroundColor: COLORS.white,
        borderTopWidth: 1,
        borderTopColor: COLORS.lightGray,
    },
    textInput: {
        flex: 1,
        borderWidth: 1,
        borderColor: COLORS.lightGray,
        borderRadius: 25,
        paddingHorizontal: 15,
        paddingVertical: 10,
        fontSize: 16,
        maxHeight: 100,
        marginRight: 10,
    },
    sendButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 25,
        width: 50,
        height: 50,
        justifyContent: 'center',
        alignItems: 'center',
    },
});

export default ChatScreen;