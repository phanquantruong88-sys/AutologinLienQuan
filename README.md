<!DOCTYPE html>
<html lang="vi" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README - APQT SYSTEM</title>
    
    <!-- Tích hợp Tailwind CSS và FontAwesome -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <style>
        body { 
            background-color: #0B0F19; 
            color: #E2E8F0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        .content-wrapper { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 40px 20px; 
        }
        h1, h2, h3 { 
            color: #38BDF8; 
            font-weight: 800; 
            margin-top: 1.5em; 
            margin-bottom: 0.5em; 
        }
        h1 { 
            font-size: 2.5rem; 
            text-align: center; 
            line-height: 1.2;
        }
        h2 { 
            font-size: 1.75rem; 
            border-bottom: 1px solid #334155; 
            padding-bottom: 10px; 
        }
        p { 
            margin-bottom: 1em; 
            line-height: 1.7; 
            font-size: 1.05rem;
        }
        ul { 
            list-style-type: none; 
            padding-left: 0; 
            margin-bottom: 1.5em; 
        }
        ul li { 
            position: relative; 
            padding-left: 1.5rem; 
            margin-bottom: 0.75em; 
            line-height: 1.6;
        }
        ul li::before { 
            content: "•"; 
            color: #38BDF8; 
            position: absolute; 
            left: 0; 
            font-weight: bold;
        }
        a { 
            color: #3B82F6; 
            text-decoration: none; 
            transition: color 0.2s;
        }
        a:hover { 
            color: #60A5FA; 
            text-decoration: underline; 
        }
        .badges { 
            display: flex; 
            justify-content: center; 
            gap: 12px; 
            margin-bottom: 30px; 
            flex-wrap: wrap; 
        }
        .badges img { 
            height: 28px; 
            border-radius: 4px;
        }
        .video-container { 
            position: relative; 
            padding-bottom: 56.25%; 
            height: 0; 
            overflow: hidden; 
            max-width: 100%; 
            background: #000; 
            border-radius: 12px; 
            border: 1px solid #334155; 
            margin: 25px 0; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        .video-container iframe { 
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
        }
        blockquote { 
            background: rgba(30, 41, 59, 0.5); 
            border-left: 4px solid #F59E0B; 
            padding: 20px; 
            margin: 25px 0; 
            border-radius: 0 8px 8px 0; 
        }
        .donate-box { 
            background: #151A25; 
            border: 1px solid #334155; 
            border-radius: 16px; 
            padding: 30px; 
            text-align: center; 
            margin-top: 40px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="content-wrapper">
        <h1>👑 APQT SYSTEM<br><span class="text-2xl text-gray-300 font-normal">Nền Tảng Tự Động Hóa Đa Thiết Bị</span></h1>
        
        <div class="badges">
            <img src="https://img.shields.io/badge/License-100%25%20FREE-brightgreen?style=for-the-badge" alt="License 100% FREE">
            <img src="https://img.shields.io/badge/Platform-Phone%20Farm%20%7C%20Giả%20Lập-blue?style=for-the-badge" alt="Platform Supported">
            <a href="https://apqt.top" target="_blank"><img src="https://img.shields.io/badge/Website-APQT.TOP-FF4500?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Official Website"></a>
            <a href="https://t.me/APQTTOP" target="_blank"><img src="https://img.shields.io/badge/Contact-@APQTTOP-2CA5E0?style=for-the-badge&logo=telegram" alt="Contact Telegram"></a>
        </div>

        <p><strong>APQT SYSTEM</strong> là bộ công cụ Auto Script đa năng giúp giải phóng hoàn toàn đôi tay của bạn. Được tối ưu hóa để điều khiển mượt mà vô số <strong>giả lập khác nhau</strong> cùng lúc, đồng thời tương thích hoàn hảo với <strong>Hệ thống Điện thoại thật (Phone Farm)</strong>.</p>
        
        <p>Dự án được chia sẻ <strong class="text-green-400">100% MIỄN PHÍ</strong>. Quản trị tập trung, an toàn tuyệt đối, kịch bản chạy độc lập. <em>(Đặc biệt: Có phiên bản Liên Quân Bypass cho ai cần)</em>.</p>

        <h2>🚀 Tính Năng Nổi Bật</h2>
        <ul>
            <li><span class="text-xl mr-2">📱</span><strong>Điều Khiển Đa Thiết Bị:</strong> Kiểm soát đồng thời hàng loạt các loại giả lập khác nhau và hệ thống điện thoại thật mà không bị chéo luồng. Quản lý tác vụ số lượng lớn cực kỳ nhẹ nhàng.</li>
            <li><span class="text-xl mr-2">👁️</span><strong>Mắt Thần Nhận Diện (AI):</strong> Công nghệ OpenCV quét màn hình với chế độ <em>Check Ảnh 60s</em>. Xử lý triệt để tình trạng lag mạng: không thấy ảnh = chờ hoặc dừng, không bao giờ click bậy.</li>
            <li><span class="text-xl mr-2">⌨️</span><strong>Tùy Biến Kịch Bản (Macro):</strong> Tự do thiết lập các bước: Click Tọa Độ, Auto điền văn bản, Lặp vòng, và Chạy nối tiếp Script khác cho cả giả lập và máy thật.</li>
            <li><span class="text-xl mr-2">🛡️</span><strong>An Toàn Tuyệt Đối:</strong> Thiết kế khép kín hoàn toàn, các luồng thực thi trực tiếp trên thiết bị của bạn thông qua môi trường cách ly.</li>
            <li><span class="text-xl mr-2">⚙️</span><strong>Kiểm Soát Ứng Dụng Sâu:</strong> Tương tác trực tiếp vào hệ thống Android: Tự động mở App theo Package Name, Xóa Data App để làm sạch cache, Cài file APK hàng loạt cho tất cả thiết bị.</li>
            <li><span class="text-xl mr-2">⚡</span><strong>Auto Thiết Lập ADB:</strong> Phần mềm thông minh tự nhận diện môi trường và tải ADB nếu cần, đảm bảo thiết bị thực và giả lập luôn sẵn sàng.</li>
        </ul>

        <h2>📺 Video Hướng Dẫn Trực Quan</h2>
        <p>Để thiết lập kịch bản Macro, kết nối các loại thiết bị (giả lập/phone thật) và vận hành hệ thống một cách trơn tru nhất, vui lòng xem kỹ video hướng dẫn dưới đây trước khi bắt đầu:</p>
        
        <div class="video-container">
            <iframe src="https://www.youtube.com/embed/_b6KOYktfbc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>

        <h2>🛠️ Các Bước Sử Dụng</h2>
        <p>Vui lòng làm theo đúng thứ tự để kết nối giả lập hoặc phone thật mượt mà nhất:</p>
        <ol class="list-decimal pl-6 mb-6 text-lg text-gray-300">
            <li class="mb-3"><strong class="text-white">Tải Công Cụ (Free):</strong> Tải toàn bộ mã nguồn của dự án này về máy tính và giải nén.</li>
            <li class="mb-3"><strong class="text-white">Học Cấu Hình:</strong> Dựa vào Video Hướng Dẫn ở trên để biết cách quét kết nối ADB cho hệ thống Phone thật hoặc các loại giả lập khác nhau.</li>
            <li class="mb-3"><strong class="text-white">Khởi Động:</strong> Mở ứng dụng, cài đặt danh sách thiết bị, nhập danh sách tài khoản và nhấn <strong class="text-blue-400">CHẠY AUTO</strong> để tận hưởng quy trình làm việc rảnh tay!</li>
        </ol>

        <blockquote>
            <h3 class="text-yellow-500 mt-0 mb-3 text-xl flex items-center gap-2"><i class="fa-solid fa-triangle-exclamation"></i> LƯU Ý KẾT NỐI ADB QUAN TRỌNG:</h3>
            <p class="m-0 text-gray-300">Bạn <strong>BẮT BUỘC</strong> phải vào phần <em>Cài đặt</em> trên Giả lập hoặc Điện thoại thật -> Bật <strong>"Chế độ gỡ lỗi USB" (ADB Debugging)</strong> để phần mềm có thể nhận diện thiết bị và tương tác điều khiển.</p>
        </blockquote>

        <h2>🔮 Định Hướng Tương Lai (Roadmap)</h2>
        <p>Chúng tôi đang không ngừng nâng cấp APQT SYSTEM trở thành cỗ máy cày cuốc công nghiệp hỗ trợ đa nền tảng phần cứng mạnh mẽ nhất:</p>
        <ul class="text-gray-300">
            <li><strong class="text-purple-400">[ 1 ] Hệ thống Auto Reg:</strong> Tự động hóa toàn diện quy trình tạo tài khoản hàng loạt trên môi trường giả lập và Phone Farm.</li>
            <li><strong class="text-blue-400">[ 2 ] Mắt thần AI Giải Captcha:</strong> Tích hợp dịch vụ Anti-Captcha. Tool tự nhìn hình, tự giải đố để vượt qua mọi hàng rào xác minh bot.</li>
            <li><strong class="text-green-400">[ 3 ] Tương thích Thiết Bị Rộng Mở:</strong> Mở rộng thuật toán ADB để nhận diện ổn định mọi dòng máy điện thoại Android, tối ưu hóa băng thông cáp kết nối.</li>
        </ul>

        <div class="donate-box">
            <h2 class="mt-0 border-none text-3xl flex items-center justify-center gap-3"><i class="fa-solid fa-mug-hot text-amber-600"></i> Ủng Hộ (Donate) Dự Án</h2>
            <p class="text-gray-400 mb-6">Dự án này được phát triển và chia sẻ hoàn toàn <strong>miễn phí</strong>. Nếu bạn thấy tool hữu ích, giúp tiết kiệm thời gian và mang lại hiệu quả công việc, bạn có thể ủng hộ để tiếp thêm động lực cho dev duy trì và phát triển thêm nhiều tính năng mới. Mọi sự đóng góp dù lớn hay nhỏ đều được trân trọng! ❤️</p>
            
            <div class="bg-[#0B0F19] p-6 rounded-xl inline-block text-left border border-gray-700 w-full md:w-auto">
                <div class="flex items-center gap-4 mb-4 pb-4 border-b border-gray-800">
                    <div class="w-12 h-12 bg-blue-900/50 rounded-lg flex items-center justify-center text-blue-400 text-2xl">
                        <i class="fa-solid fa-building-columns"></i>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500 mb-1">Ngân hàng</p>
                        <p class="font-bold text-lg text-white">KienLongBank</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-4 mb-4 pb-4 border-b border-gray-800">
                    <div class="w-12 h-12 bg-green-900/50 rounded-lg flex items-center justify-center text-green-400 text-2xl">
                        <i class="fa-solid fa-credit-card"></i>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500 mb-1">Số tài khoản</p>
                        <p class="font-bold text-2xl text-green-400 tracking-widest">24243939</p>
                    </div>
                </div>

                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-purple-900/50 rounded-lg flex items-center justify-center text-purple-400 text-2xl">
                        <i class="fa-solid fa-comment-dots"></i>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500 mb-1">Nội dung chuyển khoản</p>
                        <p class="font-bold text-lg text-white bg-gray-800 px-3 py-1 rounded inline-block">Donate APQT</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-12 text-center border-t border-gray-800 pt-8 flex flex-col items-center">
            <h2 class="border-none mt-0 text-2xl mb-2">📞 Liên Hệ & Hỗ Trợ</h2>
            <p class="text-gray-400 mb-2">Phát triển bởi <strong class="text-white">Trường Phan</strong>.</p>
            <p class="text-gray-400 mb-6">Nếu bạn có bất kỳ thắc mắc nào, vui lòng tham khảo trang web hoặc liên hệ trực tiếp qua Telegram:</p>
            
            <div class="flex flex-col sm:flex-row justify-center gap-4 w-full sm:w-auto">
                <a href="https://apqt.top" target="_blank" class="inline-flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 px-8 rounded-full transition-transform hover:-translate-y-1 shadow-lg border border-gray-700">
                    <i class="fa-solid fa-globe text-xl text-blue-400"></i> Xem Website: APQT.TOP
                </a>
                <a href="https://t.me/APQTTOP" target="_blank" class="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-8 rounded-full transition-transform hover:-translate-y-1 shadow-lg shadow-blue-500/30">
                    <i class="fa-brands fa-telegram text-2xl"></i> Liên hệ @APQTTOP
                </a>
            </div>
        </div>
    </div>
</body>
</html>
