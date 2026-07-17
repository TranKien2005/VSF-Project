# FFmpeg portable cho Windows

Candidate-mining dùng FFmpeg để đọc metadata (`ffprobe`) và export thủ công một context span đã chọn trong `browse` (`ffmpeg`): cả clean MP4 và bbox-annotated MP4. Không cần cài FFmpeg toàn hệ thống: pipeline ưu tiên binary local trong repository. Bbox rendering dùng OpenCV đã có trong extra `vision`, không cần thêm Python video library.

## Vị trí và cơ chế tìm tool

```text
tools/ffmpeg/
├── ffmpeg.exe
├── ffprobe.exe
└── LICENSE / COPYING / notices từ archive (nếu có)
```

Pipeline tìm tool theo thứ tự:

1. `tools/ffmpeg/ffmpeg.exe` và `tools/ffmpeg/ffprobe.exe`.
2. Executable tương ứng trên `PATH` nếu portable binary không tồn tại.

Pipeline không sửa `PATH` của máy. Cả hai binary local bị Git-ignore, không commit/push.

## Release đang provision local

| Thuộc tính | Giá trị |
|---|---|
| Provider | [gyan.dev FFmpeg builds](https://www.gyan.dev/ffmpeg/builds/) |
| Archive | `ffmpeg-release-essentials.7z` (~32 MB) |
| Release page ghi nhận | 8.1.2 (2026-06-27) |
| Pinned download URL | `https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z` |
| Published SHA-256 URL | `https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z.sha256` |
| SHA-256 đã kiểm tra trước giải nén | `e25b682664025d49034c981afb4bae36238a40f29a3cc1c713ad9a8b5b3528f6` |
| Build/license | 64-bit static, GPLv3 theo provider |

> Archive “essentials” có `ffmpeg`, `ffprobe` và `libx264`, đủ cho POC hiện tại. Không thay bằng build LGPL nếu chưa đổi codec/export policy.

## Kiểm tra sau khi provision

```powershell
.\tools\ffmpeg\ffmpeg.exe -hide_banner -version
.\tools\ffmpeg\ffprobe.exe -hide_banner -version
.\tools\ffmpeg\ffmpeg.exe -L
```

Xác nhận `ffmpeg.exe -encoders` có `libx264` trước khi export video thật. Giữ các license/notices đi kèm archive tại local tool directory. Nếu sau này phân phối binary ra ngoài repository, phải tuân thủ điều khoản GPL và notices của build đó.

## Provision thủ công khi cần tái tạo

1. Chỉ tải URL pinned ở trên qua HTTPS.
2. So sánh SHA-256 archive với giá trị trong bảng trước khi giải nén.
3. Kiểm tra danh sách archive trước khi giải nén.
4. Đặt `ffmpeg.exe` và `ffprobe.exe` đúng tại `tools/ffmpeg/`.
5. Chạy ba lệnh kiểm tra phía trên.

Không dùng URL “latest” hay checksum từ nguồn không phải provider cho bản release đã được pin.
