# Hành vi cần phát hiện trong hệ thống Camera AI

## 1. Phạm vi đầu vào

Đầu vào của hệ thống chỉ là một file video.

Ví dụ:

```text
input_video.mp4
```

Không giả định có sẵn:

```text
camera_id
camera_name
ROI GREEN / YELLOW / RED
khoảng cách tới camera
khoảng cách tới hàng rào
ngày / đêm
có đèn / không đèn
camera calibration
```

Những thông tin không thể xác định chắc chắn từ video phải được:

```text
AUTO_ESTIMATED
hoặc
HUMAN_CONFIRMED
```

Không được tự suy đoán thành dữ liệu chắc chắn.

---

# 2. Nguyên tắc xử lý chung

Pipeline xử lý theo hướng:

```text
1 VIDEO INPUT
    ↓
Phân tích nội dung video
    ↓
Tìm candidate hành vi
    ↓
Xác định thời điểm bắt đầu/kết thúc
    ↓
Xác định hành vi
    ↓
Bổ sung thông tin cần xác nhận qua UI nếu cần
```

Một video có thể chứa:

```text
0 hành vi
1 hành vi
nhiều hành vi
```

Một video cũng có thể có:

```text
nhiều người
nhiều event
nhiều hành vi xảy ra cùng lúc
```

Không giả định:

```text
1 video = 1 hành vi
```

---

# 3. Nhóm 1 — Trèo rào, xâm nhập

## 3.1. Lảng vảng gần hàng rào

### Mô tả

Đối tượng đi lại hoặc lưu lại lâu trong khu vực gần hàng rào.

### Điều kiện xác định

Chỉ xác định là hành vi lảng vảng khi:

```text
Có người xuất hiện
AND
đối tượng lưu lại hoặc di chuyển trong cùng khu vực
AND
thời gian > 5 phút
```

Nếu:

```text
thời gian <= 5 phút
```

thì không xác định là hành vi lảng vảng.

### Điều kiện ROI

Nếu đã có ROI được người dùng cấu hình:

```text
đối tượng nằm trong ROI GREEN
```

Nếu chưa có ROI:

```text
tool chỉ tạo candidate
người dùng xác nhận khu vực qua UI
```

### Mức cảnh báo

```text
Cấp 4 — Theo dõi
```

### Khoảng cách tới camera

Chỉ áp dụng nếu có người.

Các mức cần phân loại:

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

Vì đầu vào chỉ có video và không có calibration:

```text
tool không được tự khẳng định khoảng cách chính xác
```

Khoảng cách nên:

```text
AUTO_ESTIMATED
hoặc
HUMAN_CONFIRMED
```

### Lưu ý output

Không được cắt hành vi lảng vảng thành clip 60 giây rồi coi đó là đủ bằng chứng.

Output cần giữ được:

```text
event_start
event_end
duration > 300 giây
```

---

## 3.2. Tiếp cận hàng rào

### Mô tả

Đối tượng di chuyển tới khu vực sát hàng rào.

### Điều kiện xác định

Nếu đã có ROI:

```text
đối tượng chạm hoặc đi vào ROI YELLOW
```

Luồng điển hình:

```text
OUTSIDE
→ GREEN
→ YELLOW
```

Nếu chưa có ROI:

```text
tool phát hiện người di chuyển tới khu vực sát biên/hàng rào
→ tạo candidate
→ người dùng xác nhận trên UI
```

### Mức cảnh báo

```text
Cấp 2-3 — Cảnh báo
```

### Khoảng cách tới camera

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

Khoảng cách phải được xác nhận nếu không có calibration.

---

## 3.3. Trèo hàng rào

### Mô tả

Đối tượng leo, bám hoặc cố gắng vượt qua hàng rào.

### Các trường hợp cần phát hiện

```text
Bám vào hàng rào
Leo lên thân hàng rào
Leo lên đỉnh hàng rào
Ngồi hoặc đứng trên đỉnh hàng rào
Đưa một phần cơ thể qua hàng rào
Vượt hoàn toàn qua hàng rào
```

### Điều kiện xác định

Tool cần dựa trên:

```text
Person Detection
+
Tracking
+
Chuyển động cơ thể
+
Vị trí tương đối với hàng rào nếu xác định được
```

Nếu chưa biết chính xác vị trí hàng rào:

```text
tạo candidate
→ người dùng xác nhận trên UI
```

### Mức cảnh báo

```text
Cấp 1 — Khẩn cấp
```

### Khoảng cách tới camera

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

### Điều kiện ánh sáng

Tool có thể ước lượng:

```text
DAY
NIGHT
NIGHT_WITH_LIGHT
UNKNOWN
```

Nếu không chắc chắn:

```text
HUMAN_CONFIRMED
```

---

## 3.4. Trèo tường

### Mô tả

Đối tượng leo, bám hoặc vượt qua tường bao.

### Các trường hợp cần phát hiện

```text
Bám vào tường
Leo lên tường
Ngồi hoặc đứng trên đỉnh tường
Đưa một phần cơ thể qua tường
Vượt hoàn toàn từ ngoài vào trong
```

### Điều kiện xác định

Tool cần dựa trên:

```text
Person Detection
+
Tracking
+
Chuyển động leo/trèo
+
Vị trí tương đối với tường nếu xác định được
```

Nếu chưa biết chính xác vị trí tường:

```text
tạo candidate
→ người dùng xác nhận trên UI
```

### Mức cảnh báo

```text
Cấp 1 — Khẩn cấp
```

### Khoảng cách tới camera

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

### Điều kiện ánh sáng

```text
DAY
NIGHT
NIGHT_WITH_LIGHT
UNKNOWN
```

---

## 3.5. Xâm nhập khu cấm

### Mô tả

Đối tượng vượt vào khu vực cấm phía trong hàng rào hoặc tường bảo vệ.

### Các trường hợp cần phát hiện

```text
Đi vào vùng cấm
Vượt qua hàng rào
Vượt qua tường
Đi từ bên ngoài vào khu vực bên trong
```

Nếu đã có ROI:

```text
Chạm ROI RED
Đi vào ROI RED
```

Luồng điển hình:

```text
OUTSIDE
→ GREEN
→ YELLOW
→ RED
→ INSIDE
```

Không bắt buộc đối tượng phải đi qua đầy đủ các ROI.

Ví dụ:

```text
Đối tượng trèo trực tiếp qua hàng rào vào khu vực bên trong
→ vẫn là xâm nhập
```

### Nếu chưa có ROI

```text
tool tạo candidate từ trajectory / crossing / tracking
→ người dùng xác nhận khu vực xâm nhập trên UI
```

### Mức cảnh báo

```text
Cấp 1 — Khẩn cấp
```

### Khoảng cách tới camera

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

### Khoảng cách tới biên

Nếu không có calibration:

```text
không được tự khẳng định distance_to_boundary chính xác
```

Có thể dùng:

```text
ROI
hoặc
HUMAN_CONFIRMED
```

---

# 4. Nhóm 2 — Che camera và suy giảm hình ảnh

Các hành vi trong nhóm này không phân loại theo khoảng cách 5m-40m.

## 4.1. Camera bị che trong thời gian ngắn

### Mô tả

Toàn bộ hoặc phần lớn trường nhìn của camera bị che khuất.

### Điều kiện

```text
Camera bị che
AND
thời gian bị che < 2 phút
```

### Ví dụ

```text
Dùng tay che camera
Dùng vải hoặc vật thể che camera
Vật thể chắn trước ống kính
Một vùng lớn của frame đột ngột bị che
```

### Cần phân biệt với

```text
Mất tín hiệu
Camera offline
Video lỗi
Ban đêm quá tối
Vật thể đi ngang rất nhanh
```

---

## 4.2. Camera bị che trong thời gian dài

### Mô tả

Camera bị che liên tục trong thời gian dài.

### Điều kiện

```text
Camera bị che
AND
thời gian bị che >= 2 phút
```

### Điều kiện bắt buộc

Video phải đủ dài để xác định:

```text
duration bị che >= 120 giây
```

Nếu video kết thúc trước khi đủ 2 phút:

```text
không được kết luận CAMERA_COVERED_LONG
```

Chỉ nên xác định:

```text
CAMERA_COVERED
hoặc
UNKNOWN_DURATION
```

---

## 4.3. Mưa lớn hoặc nước làm nhòe hình

### Mô tả

Mưa lớn hoặc nước bám trên ống kính làm suy giảm chất lượng hình ảnh.

### Biểu hiện

```text
Hình ảnh bị nhòe
Giảm độ sắc nét
Mất chi tiết
Có giọt nước trên lens
Vùng ảnh bị mờ hoặc méo
Một vùng mờ tồn tại qua nhiều frame
```

### Đặc điểm quan trọng

Nước bám lens thường:

```text
vùng mờ nằm gần cùng vị trí
qua nhiều frame liên tiếp
```

### Cần phân biệt với

```text
Motion blur
Camera mất nét
Compression artifact
Bitrate thấp
Ánh sáng mạnh gây lóa
```

---

## 4.4. Ánh đèn xe quét qua camera

### Mô tả

Nguồn sáng mạnh chiếu trực tiếp hoặc quét qua camera.

### Biểu hiện

```text
Độ sáng tăng đột ngột
Xuất hiện vùng sáng mạnh
Overexposure
Mất chi tiết tạm thời
Có thể gây nhòe hình
```

### Đặc điểm

```text
Xuất hiện nhanh
Tồn tại ngắn
Sau đó hình ảnh trở lại gần trạng thái bình thường
```

### Cần phân biệt với

```text
Thay đổi ngày/đêm
Camera tự điều chỉnh exposure
Đèn cố định bật lâu dài
Mặt trời mọc/lặn
Mưa hoặc nước bám lens
```

---

# 5. Nhóm 3 — Rung lắc camera mạnh / Xoay camera

Các hành vi trong nhóm này không phân loại theo khoảng cách 5m-40m.

## 5.1. Camera bị rung lắc mạnh

### Mô tả

Camera hoặc giá đỡ bị tác động làm toàn bộ scene rung lắc.

### Biểu hiện

```text
Toàn bộ khung hình cùng dịch chuyển
Các vật thể cố định cùng dịch chuyển
Góc nhìn thay đổi nhanh qua lại
Sau đó có thể trở lại vị trí ban đầu
```

### Cần phân biệt với

```text
Người hoặc xe di chuyển
Cây rung
Mưa lớn
Motion blur
```

Điểm khác biệt:

```text
CAMERA SHAKE
→ toàn bộ scene cùng chuyển động

OBJECT MOTION
→ chỉ một phần scene thay đổi
```

---

## 5.2. Camera bị xoay lệch hướng

### Mô tả

Camera bị thay đổi góc nhìn so với scene ổn định trước đó.

### Các trường hợp

```text
Xoay trái
Xoay phải
Chúc xuống
Ngửa lên
Bị đẩy lệch khỏi vùng quan sát
```

### Điều kiện xác định

Tool nên so sánh:

```text
scene trước
vs
scene sau
```

Không yêu cầu phải có reference image bên ngoài.

Có thể lấy reference tạm thời từ:

```text
đoạn video ổn định trước khi xảy ra thay đổi
```

### Đặc điểm

```text
Scene thay đổi đáng kể
Góc nhìn mới tồn tại liên tục
Không trở lại trạng thái trước đó
```

### Phân biệt với rung

```text
RUNG
→ thay đổi nhanh, dao động, có thể quay lại

XOAY
→ thay đổi góc nhìn và duy trì trạng thái mới
```

---

# 6. Quy tắc nhiều hành vi trong cùng video

Một video có thể chứa chuỗi:

```text
Lảng vảng
→ Tiếp cận hàng rào
→ Trèo hàng rào
→ Xâm nhập
```

Đây là nhiều event khác nhau trong cùng một video.

Một video cũng có thể chứa đồng thời:

```text
Trèo hàng rào
+
Xâm nhập
```

hoặc:

```text
Che camera
+
Rung camera
```

Không được bỏ hành vi thứ hai chỉ vì đã phát hiện một hành vi trước đó.

---

# 7. Quy tắc output theo hành vi

## Hành vi thông thường

Có thể cắt clip:

```text
T - 30 giây
→
T + 30 giây
```

Áp dụng cho:

```text
Trèo hàng rào
Trèo tường
Xâm nhập
Che camera
Rung camera
Xoay camera
Mưa/nước làm nhòe
Ánh đèn gây lóa
```

---

## Hành vi lảng vảng

Không được ép thành clip 60 giây.

Phải giữ:

```text
event_start
event_end
duration > 5 phút
```

Có thể xuất:

```text
toàn bộ đoạn event
```

hoặc:

```text
một video dài đủ để chứng minh hành vi >5 phút
```

---

# 8. Checklist bắt buộc cho Dev

```text
[ ] Chỉ coi video là input ban đầu.
[ ] Không giả định có camera_id.
[ ] Không giả định có ROI.
[ ] Không giả định biết khoảng cách.
[ ] Không tự khẳng định khoảng cách theo mét nếu chưa calibration.
[ ] Không tự khẳng định DAY/NIGHT/WITH_LIGHT nếu chưa đủ tin cậy.
[ ] Cho phép human confirm trên UI.
[ ] Một video có thể có nhiều người.
[ ] Một video có thể có nhiều event.
[ ] Một video có thể có nhiều hành vi.
[ ] Chỉ xác định lảng vảng khi > 5 phút.
[ ] Không ép lảng vảng thành clip 60 giây.
[ ] Không kết luận che cam dài nếu video không đủ thời lượng để chứng minh >= 2 phút.
[ ] Không gán khoảng cách cho che cam, rung cam, xoay cam, mưa/nước, lóa đèn.
[ ] Khi thiếu thông tin, dùng unknown hoặc human confirm.
