# FFmpeg portable cho Windows

Candidate Mining dùng `ffprobe` để probe video khi import và dùng `ffmpeg` cho export MP4 do operator chủ động thực hiện. Processing không tự tạo MP4.

## Vị trí và cơ chế tìm tool

```text
tools/ffmpeg/
├── ffmpeg.exe
├── ffprobe.exe
└── LICENSE / COPYING / notices từ archive (nếu có)
```

Ứng dụng tìm tool theo thứ tự:

1. `tools/ffmpeg/ffmpeg.exe` và `tools/ffmpeg/ffprobe.exe`.
2. Executable tương ứng trên `PATH` nếu portable binary không tồn tại.

Ứng dụng không sửa `PATH` của máy. Cả hai binary local bị Git-ignore, không commit/push.

## Export hiện tại

- Export luôn là thao tác rõ ràng của operator từ giao diện.
- Export clean MP4 dùng FFmpeg.
- Export bbox MP4 dùng evidence bbox đã lưu; không gọi detector lại.
- Target export là file `.mp4`, không được ghi đè video nguồn và được tạo qua file tạm trước khi publish.

## Kiểm tra sau khi provision

```powershell
.\tools\ffmpeg\ffmpeg.exe -hide_banner -version
.\tools\ffmpeg\ffprobe.exe -hide_banner -version
.\tools\ffmpeg\ffmpeg.exe -L
```

Xác nhận `ffmpeg.exe -encoders` có `libx264` trước khi export video thật. Giữ license/notices đi kèm archive tại local tool directory. Nếu phân phối binary ra ngoài repository, phải tuân thủ điều khoản license và notices của build đang dùng.

## Provision thủ công

1. Tải archive qua HTTPS từ nguồn đã được phê duyệt.
2. Kiểm tra SHA-256 từ nguồn phát hành trước khi giải nén.
3. Kiểm tra nội dung archive trước khi giải nén.
4. Đặt `ffmpeg.exe` và `ffprobe.exe` tại `tools/ffmpeg/`.
5. Chạy các lệnh kiểm tra ở trên.

Không commit archive, binary, video nguồn hoặc export evidence vào repository.
