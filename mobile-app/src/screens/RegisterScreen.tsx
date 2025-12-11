import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import { COLORS } from '../constants/colors';

const RegisterScreen = ({ navigation }: any) => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        phone: '',
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const { register } = useAuth();

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value,
        }));
    };

    const validateForm = () => {
        const { name, email, password, confirmPassword } = formData;

        if (!name || !email || !password || !confirmPassword) {
            Alert.alert('Lỗi', 'Vui lòng nhập đầy đủ thông tin bắt buộc');
            return false;
        }

        if (password !== confirmPassword) {
            Alert.alert('Lỗi', 'Mật khẩu xác nhận không khớp');
            return false;
        }

        if (password.length < 6) {
            Alert.alert('Lỗi', 'Mật khẩu phải có ít nhất 6 ký tự');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            Alert.alert('Lỗi', 'Email không hợp lệ');
            return false;
        }

        return true;
    };

    const handleRegister = async () => {
        if (!validateForm()) return;

        setIsLoading(true);
        const { confirmPassword, ...registerData } = formData;
        const success = await register(registerData);
        setIsLoading(false);

        if (!success) {
            Alert.alert('Lỗi', 'Đăng ký thất bại. Vui lòng thử lại');
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <LinearGradient
                colors={[COLORS.gradientStart, COLORS.gradientEnd]}
                style={styles.gradient}
            >
                <ScrollView contentContainerStyle={styles.scrollContent}>
                    <View style={styles.header}>
                        <TouchableOpacity
                            style={styles.backButton}
                            onPress={() => navigation.goBack()}
                        >
                            <Icon name="arrow-back" size={24} color={COLORS.white} />
                        </TouchableOpacity>
                        <Text style={styles.title}>Tạo tài khoản</Text>
                        <Text style={styles.subtitle}>Tham gia cộng đồng sức khỏe</Text>
                    </View>

                    <View style={styles.formContainer}>
                        <View style={styles.inputContainer}>
                            <Icon name="person" size={24} color={COLORS.gray} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Họ và tên *"
                                placeholderTextColor={COLORS.gray}
                                value={formData.name}
                                onChangeText={(value) => handleInputChange('name', value)}
                                autoCapitalize="words"
                            />
                        </View>

                        <View style={styles.inputContainer}>
                            <Icon name="email" size={24} color={COLORS.gray} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Email *"
                                placeholderTextColor={COLORS.gray}
                                value={formData.email}
                                onChangeText={(value) => handleInputChange('email', value)}
                                keyboardType="email-address"
                                autoCapitalize="none"
                                autoCorrect={false}
                            />
                        </View>

                        <View style={styles.inputContainer}>
                            <Icon name="phone" size={24} color={COLORS.gray} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Số điện thoại"
                                placeholderTextColor={COLORS.gray}
                                value={formData.phone}
                                onChangeText={(value) => handleInputChange('phone', value)}
                                keyboardType="phone-pad"
                            />
                        </View>

                        <View style={styles.inputContainer}>
                            <Icon name="lock" size={24} color={COLORS.gray} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Mật khẩu *"
                                placeholderTextColor={COLORS.gray}
                                value={formData.password}
                                onChangeText={(value) => handleInputChange('password', value)}
                                secureTextEntry={!showPassword}
                                autoCapitalize="none"
                            />
                            <TouchableOpacity
                                style={styles.eyeIcon}
                                onPress={() => setShowPassword(!showPassword)}
                            >
                                <Icon
                                    name={showPassword ? 'visibility' : 'visibility-off'}
                                    size={24}
                                    color={COLORS.gray}
                                />
                            </TouchableOpacity>
                        </View>

                        <View style={styles.inputContainer}>
                            <Icon name="lock-outline" size={24} color={COLORS.gray} style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Xác nhận mật khẩu *"
                                placeholderTextColor={COLORS.gray}
                                value={formData.confirmPassword}
                                onChangeText={(value) => handleInputChange('confirmPassword', value)}
                                secureTextEntry={!showConfirmPassword}
                                autoCapitalize="none"
                            />
                            <TouchableOpacity
                                style={styles.eyeIcon}
                                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                            >
                                <Icon
                                    name={showConfirmPassword ? 'visibility' : 'visibility-off'}
                                    size={24}
                                    color={COLORS.gray}
                                />
                            </TouchableOpacity>
                        </View>

                        <TouchableOpacity
                            style={styles.registerButton}
                            onPress={handleRegister}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <ActivityIndicator color={COLORS.white} />
                            ) : (
                                <Text style={styles.registerButtonText}>Đăng ký</Text>
                            )}
                        </TouchableOpacity>

                        <View style={styles.loginContainer}>
                            <Text style={styles.loginText}>Đã có tài khoản? </Text>
                            <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                                <Text style={styles.loginLink}>Đăng nhập</Text>
                            </TouchableOpacity>
                        </View>

                        <Text style={styles.termsText}>
                            Bằng việc đăng ký, bạn đồng ý với{' '}
                            <Text style={styles.termsLink}>Điều khoản sử dụng</Text>
                            {' '}và{' '}
                            <Text style={styles.termsLink}>Chính sách bảo mật</Text>
                        </Text>
                    </View>
                </ScrollView>
            </LinearGradient>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    gradient: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        padding: 20,
        paddingTop: 50,
    },
    header: {
        alignItems: 'center',
        marginBottom: 30,
        position: 'relative',
    },
    backButton: {
        position: 'absolute',
        left: 0,
        top: 0,
        padding: 10,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: COLORS.white,
        marginTop: 20,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.white,
        opacity: 0.9,
        marginTop: 8,
    },
    formContainer: {
        backgroundColor: COLORS.white,
        borderRadius: 20,
        padding: 30,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
        elevation: 5,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        borderBottomWidth: 1,
        borderBottomColor: COLORS.lightGray,
        marginBottom: 20,
        paddingBottom: 10,
    },
    inputIcon: {
        marginRight: 15,
    },
    input: {
        flex: 1,
        fontSize: 16,
        color: COLORS.textPrimary,
    },
    eyeIcon: {
        padding: 5,
    },
    registerButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 25,
        paddingVertical: 15,
        alignItems: 'center',
        marginTop: 20,
    },
    registerButtonText: {
        color: COLORS.white,
        fontSize: 18,
        fontWeight: 'bold',
    },
    loginContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 20,
    },
    loginText: {
        color: COLORS.gray,
        fontSize: 16,
    },
    loginLink: {
        color: COLORS.primary,
        fontSize: 16,
        fontWeight: 'bold',
    },
    termsText: {
        textAlign: 'center',
        color: COLORS.gray,
        fontSize: 12,
        marginTop: 20,
        lineHeight: 18,
    },
    termsLink: {
        color: COLORS.primary,
        textDecorationLine: 'underline',
    },
});

export default RegisterScreen;