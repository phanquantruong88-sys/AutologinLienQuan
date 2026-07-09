<div align="center">
  <h1>🎮 AUTO LIÊN QUÂN V2</h1>
  <p><b>Công cụ Tự Động Hóa Đa Luồng (ADB & OpenCV Macro)</b></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv" alt="OpenCV">
    <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows" alt="Windows">
  </p>
</div>

<hr>

## 🌟 Giới Thiệu

**Auto Liên Quân V2** là phần mềm hỗ trợ tự động hóa mạnh mẽ thông qua **ADB** và nhận diện hình ảnh **OpenCV**. Tool cho phép điều khiển song song nhiều giả lập LDPlayer hoặc thiết bị Android thật, hỗ trợ người dùng thiết lập và chạy các kịch bản (macro) quản lý tài khoản một cách tự động.

## 🚀 Tính Năng Nổi Bật

<table>
  <tr>
    <td align="center" width="150"><b>🎛️ Đa Luồng</b></td>
    <td>Điều khiển hàng loạt tab LDPlayer hoặc Phone thật cùng lúc mà không bị xung đột lệnh ADB.</td>
  </tr>
  <tr>
    <td align="center"><b>👁️ Nhận Diện (AI)</b></td>
    <td>Tự động tìm kiếm và click chính xác dựa trên ảnh mẫu nhờ OpenCV (kèm tính năng Timeout, Retry, Wait 60s).</td>
  </tr>
  <tr>
    <td align="center"><b>📝 Quản Lý Data</b></td>
    <td>Thêm, sửa, xóa, nhập danh sách tài khoản siêu tốc qua `.txt`, `.xlsx`. Hiển thị trực quan trạng thái <i>Thành công/Thất bại</i>.</td>
  </tr>
  <tr>
    <td align="center"><b>🛠️ Trình Macro</b></td>
    <td>Hỗ trợ: Click Tọa độ, Nhập Text tự động, Mở/Xóa data App, Cài APK, Vòng lặp và gọi Script phụ.</td>
  </tr>
</table>

<details>
<summary><b>🔧 YÊU CẦU HỆ THỐNG (Click để mở)</b></summary>
<br>

* **Hệ điều hành:** Windows 10/11
* **Môi trường:** Python 3.8 trở lên
* **Thiết bị:** LDPlayer (khuyên dùng bản 9) hoặc Điện thoại Android bật sẵn Gỡ lỗi USB (USB Debugging).
* **Thư viện phụ thuộc:** Tool tự động kiểm tra và cài đặt (`opencv-python`, `numpy`, `Pillow`, `pandas`...) trong lần chạy đầu tiên.

</details>

<hr>

## 💻 Hướng Dẫn Sử Dụng

### Bước 1: Khởi động
Mở CMD/Terminal tại thư mục chứa source code và chạy lệnh:
```bash
python app.py