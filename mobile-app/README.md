# Food Advisor Mobile App

Ứng dụng di động tư vấn dinh dưỡng thông minh với AI, được phát triển bằng React Native và Expo.

## Tính năng chính

### 🍽️ Tính toán calo qua hình ảnh
- Chụp ảnh món ăn hoặc chọn từ thư viện
- AI phân tích thành phần dinh dưỡng tự động
- Hiển thị kết quả với biểu đồ trực quan
- Lưu vào lịch sử ăn uống

### 🤖 Chatbot tư vấn dinh dưỡng
- AI chatbot thông minh tích hợp
- Tư vấn chế độ ăn theo bệnh lý
- Gợi ý thực đơn phù hợp
- Cảnh báo thực phẩm cần tránh

### 👨‍🍳 Tạo công thức nấu ăn
- Nhận diện nguyên liệu qua hình ảnh
- Gợi ý công thức từ nguyên liệu có sẵn
- Tính toán giá trị dinh dưỡng
- Hướng dẫn nấu ăn chi tiết

### 👤 Quản lý thông tin sức khỏe
- Đăng ký/đăng nhập bảo mật
- Quản lý tiền sử bệnh lý
- Theo dõi chỉ số sức khỏe (BMI, huyết áp...)
- Đặt mục tiêu dinh dưỡng cá nhân

### 🔔 Thông báo thông minh
- Nhắc nhở bữa ăn và uống thuốc
- Lời khuyên sức khỏe hàng ngày
- Báo cáo dinh dưỡng tuần
- Cài đặt thông báo linh hoạt

## Công nghệ sử dụng

- **React Native** với Expo SDK 49
- **TypeScript** cho type safety
- **React Navigation** cho điều hướng
- **Expo Camera** cho chụp ảnh
- **React Native Chart Kit** cho biểu đồ
- **Expo Notifications** cho thông báo
- **AsyncStorage & SecureStore** cho lưu trữ
- **Axios** cho API calls

## Cài đặt và chạy

### Yêu cầu hệ thống
- Node.js 16+ 
- npm hoặc yarn
- Expo CLI
- Android Studio (cho Android) hoặc Xcode (cho iOS)

### Cài đặt dependencies
```bash
cd foodadvisor-agent/mobile-app
npm install
```

### Chạy ứng dụng
```bash
# Chạy trên Expo Go
npm start

# Chạy trên Android emulator
npm run android

# Chạy trên iOS simulator
npm run ios

# Chạy trên web
npm run web
```

## Cấu trúc dự án

```
mobile-app/
├── App.tsx                 # Entry point
├── src/
│   ├── screens/           # Các màn hình
│   │   ├── HomeScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   ├── CameraScreen.tsx
│   │   ├── ChatScreen.tsx
│   │   ├── RecipeScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── HealthInfoScreen.tsx
│   │   └── NotificationScreen.tsx
│   ├── contexts/          # React Context
│   │   ├── AuthContext.tsx
│   │   └── HealthContext.tsx
│   ├── services/          # API services
│   │   └── apiService.ts
│   └── constants/         # Hằng số
│       └── colors.ts
├── assets/               # Hình ảnh, fonts
├── package.json
└── app.json             # Cấu hình Expo
```

## Kết nối Backend

Ứng dụng kết nối với FastAPI backend qua REST API:

- **Base URL**: `http://localhost:8000` (development)
- **Authentication**: JWT tokens
- **Endpoints**:
  - `/auth/login` - Đăng nhập
  - `/auth/register` - Đăng ký
  - `/calculate-calories` - Phân tích món ăn
  - `/chat` - Chatbot AI
  - `/generate-recipe` - Tạo công thức
  - `/health/*` - Quản lý sức khỏe

## Tính năng bảo mật

- JWT authentication với refresh tokens
- Mã hóa dữ liệu nhạy cảm với SecureStore
- Validation đầu vào nghiêm ngặt
- HTTPS cho tất cả API calls
- Bảo vệ thông tin y tế cá nhân

## Hỗ trợ offline

- Lưu trữ dữ liệu cơ bản offline
- Đồng bộ khi có kết nối
- Cache hình ảnh và kết quả phân tích
- Hoạt động cơ bản không cần internet

## Tối ưu hóa hiệu năng

- Lazy loading cho các màn hình
- Image optimization và caching
- Debounced search và input
- Efficient re-rendering với React.memo
- Background task cho đồng bộ dữ liệu

## Build và Deploy

### Android APK
```bash
expo build:android
```

### iOS IPA
```bash
expo build:ios
```

### Expo Updates
```bash
expo publish
```

## Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

MIT License - xem file LICENSE để biết thêm chi tiết.

## Liên hệ

- Email: support@foodadvisor.com
- Website: https://foodadvisor.com
- GitHub: https://github.com/foodadvisor/mobile-app