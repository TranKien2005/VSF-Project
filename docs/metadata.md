# Metadata Contract cho Pipeline Dataset Camera AI

## 1. Phạm vi đầu vào

Đầu vào của hệ thống chỉ gồm các file video.

Ví dụ:

```text
input/
├── video_001.mp4
├── video_002.mp4
├── video_003.mkv
└── video_004.avi
```

Không giả định hệ thống có sẵn:

```text
camera_id
camera_name
camera_model
camera_serial
camera_location
ROI
khoảng cách tới camera
khoảng cách tới hàng rào
timestamp thực tế
thông tin ngày/đêm
thông tin có đèn/không đèn
```

Nếu các thông tin trên không thể lấy trực tiếp hoặc suy ra đủ tin cậy từ video:

```text
không tự tạo dữ liệu giả
không tự suy đoán chắc chắn
```

Phải dùng:

```text
null
unknown
AUTO_ESTIMATED
HUMAN_CONFIRMED
```

tùy từng trường hợp.

---

# 2. Nguyên tắc nguồn dữ liệu

Mỗi metadata phải có nguồn.

Các giá trị hợp lệ:

```text
VIDEO_FILE
AUTO_EXTRACTED
AUTO_ESTIMATED
HUMAN_CONFIRMED
DERIVED
UNKNOWN
```

Ý nghĩa:

| Source | Ý nghĩa |
|---|---|
| `VIDEO_FILE` | Lấy trực tiếp từ file video hoặc ffprobe |
| `AUTO_EXTRACTED` | Tool lấy tự động từ nội dung video với độ chắc chắn cao |
| `AUTO_ESTIMATED` | Tool ước lượng, chưa nên coi là Ground Truth |
| `HUMAN_CONFIRMED` | Người dùng xác nhận qua UI |
| `DERIVED` | Tính từ metadata khác |
| `UNKNOWN` | Không đủ thông tin để xác định |

Mọi field được AI/CV suy ra nên có thêm:

```text
confidence
source
```

---

# 3. Quan hệ dữ liệu

Pipeline phải hỗ trợ:

```text
1 source video
    ↓
0..n objects
    ↓
0..n events
    ↓
0..n output clips
```

Không được giả định:

```text
1 video = 1 camera chắc chắn
1 video = 1 người
1 video = 1 hành vi
1 clip = 1 hành vi
```

Một video có thể chứa:

```text
nhiều người
nhiều hành vi
nhiều event tại các thời điểm khác nhau
```

Một clip có thể chứa:

```text
2-3 hoặc nhiều hành vi
```

---

# 4. Metadata cấp Video

Mỗi file video phải có một record.

## Field bắt buộc

```text
video_id
source_path
filename
file_extension
file_size_bytes
file_mtime
duration_seconds
fps
width
height
codec
container
bit_rate
creation_time
creation_time_source
decode_status
source_fingerprint
processing_status
```

---

## 4.1. `video_id`

ID duy nhất do hệ thống sinh.

Ví dụ:

```text
VID_000001
```

Nguồn:

```text
DERIVED
```

Không lấy `video_id` từ camera hoặc model camera.

---

## 4.2. `source_path`

Đường dẫn tới video gốc.

Ví dụ:

```text
input/video_001.mp4
```

Nguồn:

```text
VIDEO_FILE
```

Raw video phải được coi là immutable.

Không:

```text
overwrite
rename tự động
move
delete
```

nếu chưa có thao tác rõ ràng của pipeline.

---

## 4.3. `filename`

Tên file video.

Ví dụ:

```text
video_001.mp4
```

Nguồn:

```text
VIDEO_FILE
```

---

## 4.4. `file_extension`

Ví dụ:

```text
.mp4
.mkv
.avi
.mov
```

---

## 4.5. `file_size_bytes`

Dung lượng file.

Nguồn:

```text
VIDEO_FILE
```

Dùng cho:

```text
inventory
performance benchmark
duplicate detection sơ bộ
```

---

## 4.6. `file_mtime`

Thời điểm file được sửa lần cuối trên filesystem.

Không coi đây là thời gian camera quay video.

Nguồn:

```text
VIDEO_FILE
```

---

## 4.7. `duration_seconds`

Thời lượng video.

Nguồn:

```text
ffprobe
```

Kiểu:

```text
float
```

---

## 4.8. `fps`

Frame per second.

Nguồn:

```text
ffprobe
```

Kiểu:

```text
float
```

---

## 4.9. `width`

Chiều rộng video theo pixel.

---

## 4.10. `height`

Chiều cao video theo pixel.

---

## 4.11. `codec`

Ví dụ:

```text
h264
h265
hevc
```

---

## 4.12. `container`

Ví dụ:

```text
mp4
mkv
avi
mov
```

---

## 4.13. `bit_rate`

Bitrate video nếu lấy được từ ffprobe.

Nếu không có:

```text
null
```

---

## 4.14. `creation_time`

Thời điểm quay video nếu metadata nhúng trong video có thông tin đáng tin cậy.

Nếu không có:

```text
null
```

Không dùng `file_mtime` thay thế cho `creation_time`.

---

## 4.15. `creation_time_source`

Giá trị:

```text
VIDEO_METADATA
FILENAME_PARSED
HUMAN_CONFIRMED
UNKNOWN
```

Chỉ parse timestamp từ filename khi format tên file rõ ràng và được user/dev cấu hình.

Không tự đoán format filename.

---

## 4.16. `decode_status`

Giá trị:

```text
OK
WARNING
FAILED
```

---

## 4.17. `source_fingerprint`

Fingerprint nhẹ dùng cho:

```text
cache
resume
duplicate detection
```

Khuyến nghị:

```text
file_size_bytes
+
file_mtime
+
partial hash đầu file
+
partial hash cuối file
```

Không cần full SHA256 cho toàn bộ dữ liệu lớn nếu chưa cần.

---

## 4.18. `processing_status`

Giá trị:

```text
PENDING
PROCESSING
DONE
FAILED
```

Dùng để hỗ trợ resume khi xử lý dataset lớn.

---

# 5. Metadata nhận diện Camera từ Video

Vì input chỉ có video nên không được giả định biết camera nào quay video.

Các field:

```text
camera_id
camera_id_source
camera_group_confidence
camera_model
camera_model_source
```

---

## 5.1. `camera_id`

Giá trị mặc định:

```text
unknown
```

Nếu toàn bộ batch chắc chắn chỉ có một camera, có thể gán:

```text
CAM_01
```

Nếu batch chứa video từ nhiều camera nhưng không có metadata camera:

Tool có thể thử nhóm video theo:

```text
scene similarity
background features
reference frame similarity
stable visual landmarks
```

Ví dụ:

```text
Cluster A → CAM_01
Cluster B → CAM_02
Cluster C → CAM_03
```

Nhưng kết quả này chỉ là:

```text
AUTO_ESTIMATED
```

và nên được người dùng xác nhận trên UI.

Không được suy ra `camera_id` từ:

```text
video resolution
codec
fps
```

vì nhiều camera có thể có cùng thông số.

---

## 5.2. `camera_id_source`

Giá trị:

```text
AUTO_ESTIMATED
HUMAN_CONFIRMED
UNKNOWN
```

---

## 5.3. `camera_group_confidence`

Confidence khi tool tự nhóm video theo camera.

Range:

```text
0.0 → 1.0
```

Nếu user xác nhận:

```text
camera_id_source = HUMAN_CONFIRMED
```

---

## 5.4. `camera_model`

Chỉ lấy nếu video có embedded metadata rõ ràng.

Nếu không:

```text
null
```

Không tự gán model camera dựa trên thông tin ngoài video.

---

# 6. Metadata cấp Object / Person

Mỗi người được detect và tracking phải có record riêng.

Các field:

```text
object_id
video_id
track_id
object_type
first_seen
last_seen
track_duration_seconds
max_confidence
avg_confidence
distance_to_camera
distance_to_camera_source
current_roi
roi_history
```

---

## 6.1. `object_id`

ID duy nhất trong toàn dataset.

Ví dụ:

```text
OBJ_VID000001_0001
```

---

## 6.2. `track_id`

ID từ tracker trong phạm vi một video.

Ví dụ:

```text
1
2
3
```

`track_id` có thể trùng giữa hai video khác nhau.

`object_id` không được trùng.

---

## 6.3. `object_type`

Trong scope hiện tại:

```text
PERSON
```

Có thể mở rộng:

```text
VEHICLE
ANIMAL
UNKNOWN
```

---

## 6.4. `first_seen`

Thời điểm xuất hiện đầu tiên.

Đơn vị:

```text
seconds from video start
```

---

## 6.5. `last_seen`

Thời điểm xuất hiện cuối cùng.

---

## 6.6. `track_duration_seconds`

Tính:

```text
last_seen - first_seen
```

---

## 6.7. `max_confidence`

Confidence detect người cao nhất trong track.

Range:

```text
0.0 → 1.0
```

---

## 6.8. `avg_confidence`

Confidence trung bình của track.

---

# 7. Metadata khoảng cách tới Camera

Các mức khoảng cách nghiệp vụ:

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

Vì input chỉ có video và không có camera calibration nên:

```text
tool không được tự khẳng định khoảng cách chính xác bằng mét
```

trừ khi có đủ điều kiện hình học/calibration.

---

## 7.1. `distance_to_camera`

Chỉ áp dụng cho hành vi có người:

```text
Lảng vảng gần hàng rào
Tiếp cận hàng rào
Trèo hàng rào
Trèo tường
Xâm nhập
```

Giá trị hợp lệ:

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

Nếu chưa xác định:

```text
unknown
```

Với hành vi không liên quan tới khoảng cách người:

```text
Che camera
Rung camera
Xoay camera
Mưa/nước làm nhòe
Ánh đèn gây lóa
```

dùng:

```text
null
```

---

## 7.2. `distance_to_camera_source`

Giá trị:

```text
AUTO_ESTIMATED
HUMAN_CONFIRMED
UNKNOWN
```

Khuyến nghị giai đoạn hiện tại:

```text
HUMAN_CONFIRMED
```

qua UI.

---

## 7.3. Lưu ý quan trọng

Một người có thể di chuyển trong video.

Vì vậy:

```text
distance_to_camera
```

không nhất thiết cố định trong toàn bộ track.

Khoảng cách nên gắn theo:

```text
event
```

hoặc thời điểm quan trọng.

---

# 8. Metadata ROI

Vì input chỉ có video nên ROI không tồn tại sẵn.

Tool không được tự giả định:

```text
GREEN
YELLOW
RED
```

Nếu cần dùng ROI:

```text
1. Lấy frame đại diện từ video.
2. Hiển thị trên UI.
3. Người dùng vẽ ROI.
4. Lưu ROI cho nhóm video cùng camera.
```

Các field:

```text
roi_config_id
roi_source
roi_green
roi_yellow
roi_red
fence_line
wall_line
```

Nguồn hợp lệ:

```text
HUMAN_CONFIRMED
AUTO_ESTIMATED
UNKNOWN
```

Khuyến nghị:

```text
HUMAN_CONFIRMED
```

---

## 8.1. `current_roi`

Giá trị:

```text
OUTSIDE
GREEN
YELLOW
RED
INSIDE
UNKNOWN
```

Chỉ xác định khi đã có ROI config.

Nếu chưa có ROI:

```text
UNKNOWN
```

---

## 8.2. `roi_history`

Ví dụ:

```json
[
  {
    "roi": "GREEN",
    "start": 10.5,
    "end": 320.2
  },
  {
    "roi": "YELLOW",
    "start": 320.2,
    "end": 330.0
  },
  {
    "roi": "RED",
    "start": 330.0,
    "end": 345.0
  }
]
```

---

# 9. Metadata cấp Event

Mỗi hành vi là một event riêng.

Các field:

```text
event_id
video_id
object_id
camera_id
behavior_code
event_start
event_end
event_time
event_time_source
trigger_time
duration_seconds
roi_zone
distance_to_camera
distance_to_camera_source
time_of_day
time_of_day_source
lighting_condition
lighting_condition_source
confidence
detection_source
review_status
```

---

## 9.1. `event_id`

ID duy nhất.

Ví dụ:

```text
EVT_VID000001_0001
```

---

## 9.2. `behavior_code`

Mã hành vi ổn định dùng trong code.

Ví dụ:

```text
LOITERING
APPROACH_FENCE
FENCE_CLIMBING
WALL_CLIMBING
INTRUSION
CAMERA_COVERED_SHORT
CAMERA_COVERED_LONG
WATER_BLUR
HEADLIGHT_GLARE
CAMERA_SHAKE
CAMERA_ROTATION
```

Một event chỉ đại diện cho một hành vi.

Nếu cùng thời điểm có:

```text
FENCE_CLIMBING
+
INTRUSION
```

thì tạo:

```text
2 event_id
```

---

## 9.3. `event_start`

Thời điểm bắt đầu hành vi.

Đơn vị:

```text
seconds from source video start
```

---

## 9.4. `event_end`

Thời điểm kết thúc hành vi.

---

## 9.5. `event_time`

Thời điểm đại diện cho event.

Kiểu:

```text
float
```

Ví dụ:

```text
330.0
```

Không được lưu text như:

```text
HUMAN_CONFIRMED
```

vào field này.

---

## 9.6. `event_time_source`

Giá trị:

```text
AUTO_EXTRACTED
AUTO_ESTIMATED
HUMAN_CONFIRMED
UNKNOWN
```

---

## 9.7. `trigger_time`

Thời điểm event đạt điều kiện nghiệp vụ.

Ví dụ với lảng vảng:

```text
event_start = 100.0
trigger_time > 400.0
```

vì đối tượng phải lảng vảng hơn 5 phút mới được xác định.

---

## 9.8. `duration_seconds`

Tính:

```text
event_end - event_start
```

---

## 9.9. `roi_zone`

Chỉ áp dụng khi đã có ROI config.

Giá trị:

```text
GREEN
YELLOW
RED
INSIDE
UNKNOWN
null
```

Dùng:

```text
null
```

nếu hành vi không liên quan ROI.

---

## 9.10. `time_of_day`

Giá trị:

```text
DAY
NIGHT
UNKNOWN
```

Tool có thể ước lượng dựa trên hình ảnh.

Nhưng vì chỉ có video:

```text
time_of_day_source = AUTO_ESTIMATED
```

cho tới khi được user xác nhận.

---

## 9.11. `lighting_condition`

Giá trị:

```text
DAYLIGHT
NIGHT_NO_LIGHT
NIGHT_WITH_LIGHT
STRONG_GLARE
UNKNOWN
```

Với video không đủ chắc chắn:

```text
UNKNOWN
```

---

## 9.12. `confidence`

Confidence của detector hoặc event engine.

Range:

```text
0.0 → 1.0
```

Nếu event do người tạo hoàn toàn trên UI:

```text
confidence = null
detection_source = HUMAN
```

Không dùng:

```text
confidence = 1.0
```

chỉ để biểu diễn rằng con người đã xác nhận.

---

## 9.13. `detection_source`

Giá trị:

```text
AUTO
HUMAN
AUTO_AND_HUMAN
```

---

## 9.14. `review_status`

Giá trị:

```text
DRAFT
VERIFIED
REJECTED
```

Chỉ event:

```text
VERIFIED
```

được đưa vào dataset chính thức.

---

# 10. Metadata riêng cho Lảng vảng

Chỉ tạo event lảng vảng khi:

```text
duration_seconds > 300
```

Tức:

```text
> 5 phút
```

Nếu:

```text
duration_seconds <= 300
```

thì không tạo event `LOITERING`.

Các field chính:

```text
object_id
event_start
event_end
trigger_time
duration_seconds
distance_to_camera
roi_zone
```

Nếu chưa có ROI:

```text
roi_zone = UNKNOWN
```

---

# 11. Metadata riêng cho Camera bị Che

Các field bổ sung:

```text
covered_ratio
covered_duration_seconds
coverage_type
```

---

## 11.1. `covered_ratio`

Tỷ lệ frame bị che.

Range:

```text
0.0 → 1.0
```

Ví dụ:

```text
0.85
```

---

## 11.2. `coverage_type`

Giá trị:

```text
PARTIAL
FULL
UNKNOWN
```

---

## 11.3. Phân loại thời gian

```text
< 120 giây
→ CAMERA_COVERED_SHORT

>= 120 giây
→ CAMERA_COVERED_LONG
```

---

# 12. Metadata riêng cho Mưa/Nước làm Nhòe

Các field:

```text
blur_score
baseline_blur_score
blur_ratio
affected_area_ratio
water_region_persistent
```

---

## 12.1. `blur_score`

Điểm sắc nét của frame/window hiện tại.

Có thể dùng:

```text
Variance of Laplacian
```

---

## 12.2. `baseline_blur_score`

Baseline phải được tính từ các đoạn video được đánh giá là bình thường của cùng camera.

Nếu chưa xác định được camera group:

```text
baseline_blur_score = null
```

---

## 12.3. `blur_ratio`

Tính:

```text
blur_score / baseline_blur_score
```

Nếu không có baseline:

```text
null
```

---

## 12.4. `affected_area_ratio`

Tỷ lệ vùng frame bị ảnh hưởng.

Range:

```text
0.0 → 1.0
```

---

## 12.5. `water_region_persistent`

Giá trị:

```text
true
false
unknown
```

Dùng để nhận biết vùng mờ cố định qua nhiều frame.

---

# 13. Metadata riêng cho Ánh đèn/Lóa

Các field:

```text
mean_brightness
baseline_brightness
brightness_ratio
overexposed_ratio
brightness_delta
glare_duration_seconds
```

Nếu không có baseline đáng tin cậy:

```text
baseline_brightness = null
brightness_ratio = null
```

Vẫn có thể dùng:

```text
brightness_delta
overexposed_ratio
```

để tìm candidate.

---

# 14. Metadata riêng cho Camera Rung

Các field:

```text
global_motion_score
translation_x
translation_y
rotation_delta
shake_duration_seconds
returns_to_reference
```

`returns_to_reference`:

```text
true
false
unknown
```

Nếu chưa có reference frame ổn định:

```text
unknown
```

---

# 15. Metadata riêng cho Camera Xoay

Các field:

```text
reference_similarity
homography_shift
rotation_angle_estimate
scene_change_score
persistent_shift_seconds
returns_to_reference
```

Reference frame phải được lấy từ video và được xác nhận là góc nhìn bình thường.

Nếu chưa có reference:

```text
reference_similarity = null
```

Không tự chọn một frame bất thường làm reference lâu dài.

---

# 16. Metadata cấp Clip Output

Các field:

```text
clip_id
clip_path
video_id
camera_id
clip_start
clip_end
duration_seconds
event_ids
behavior_codes
behavior_count
multi_event
multi_behavior
distance_values
qc_status
```

---

## 16.1. `event_ids`

Danh sách event trong clip.

Ví dụ:

```json
[
  "EVT_001",
  "EVT_002"
]
```

---

## 16.2. `behavior_codes`

Danh sách hành vi trong clip.

Ví dụ:

```json
[
  "FENCE_CLIMBING",
  "INTRUSION"
]
```

---

## 16.3. `behavior_count`

Số loại hành vi khác nhau trong clip.

---

## 16.4. `multi_event`

```text
true
```

khi clip chứa nhiều hơn một event.

---

## 16.5. `multi_behavior`

```text
true
```

khi clip chứa nhiều hơn một loại hành vi.

Hai khái niệm này khác nhau.

Ví dụ:

```text
2 event FENCE_CLIMBING
→ multi_event = true
→ multi_behavior = false
```

Ví dụ:

```text
FENCE_CLIMBING + INTRUSION
→ multi_event = true
→ multi_behavior = true
```

---

# 17. Quy tắc độ dài Clip

Không được giả định mọi output clip đều 60 giây.

## Event thông thường

Ví dụ:

```text
Trèo rào
Trèo tường
Xâm nhập
Che cam
Rung cam
Xoay cam
Lóa đèn
Nhòe do mưa
```

Có thể cắt:

```text
T - 30 giây
→
T + 30 giây
```

Mục tiêu:

```text
60 giây
```

---

## Lảng vảng

Vì hành vi chỉ được xác định khi:

```text
> 5 phút
```

nên output lảng vảng phải giữ đủ bằng chứng thời gian.

Khuyến nghị:

```text
event_start
→
event_end
```

và đảm bảo:

```text
duration_seconds > 300
```

Không cắt lảng vảng thành clip 60 giây rồi coi đó là đủ Ground Truth cho hành vi >5 phút.

---

# 18. Metadata xử lý Pipeline

Các field:

```text
processing_status
processing_started_at
processing_finished_at
processing_seconds
processing_version
error_code
error_message
```

Dùng để:

```text
resume pipeline
tránh xử lý lại dữ liệu lớn
debug
benchmark performance
```

---

# 19. Quy tắc `null` và `unknown`

Dùng:

```text
null
```

khi field không áp dụng.

Ví dụ:

```text
CAMERA_SHAKE
→ distance_to_camera = null
```

Dùng:

```text
unknown
```

khi field có ý nghĩa nhưng chưa xác định được.

Ví dụ:

```text
FENCE_CLIMBING
→ distance_to_camera = unknown
```

Không dùng:

```text
0m
N/A
-
none
```

---

# 20. Output Metadata

Khuyến nghị:

```text
outputs/video_metadata.jsonl
outputs/object_metadata.jsonl
outputs/event_metadata.jsonl
outputs/clip_metadata.jsonl
```

Có thể sinh CSV để kiểm tra nhanh:

```text
outputs/video_metadata.csv
outputs/event_metadata.csv
outputs/clip_metadata.csv
```

JSONL là source of truth cho:

```text
array
multi-event
multi-behavior
roi_history
event_ids
distance_values
```

---

# 21. Checklist bắt buộc cho Dev Tool

```text
[ ] Chỉ coi video là input ban đầu.
[ ] Không giả định đã biết camera_id.
[ ] Không giả định đã biết model/serial camera.
[ ] Không giả định đã có ROI.
[ ] Không tự suy đoán khoảng cách chính xác bằng mét nếu chưa calibration.
[ ] Không tự coi file_mtime là thời gian quay.
[ ] Không giả định 1 video chỉ có 1 người.
[ ] Không giả định 1 video chỉ có 1 hành vi.
[ ] Không giả định 1 clip chỉ có 1 event.
[ ] Không gán khoảng cách cho hành vi không liên quan khoảng cách.
[ ] Chỉ tạo LOITERING khi thời gian > 5 phút.
[ ] Không ép LOITERING thành clip 60 giây.
[ ] Phân biệt multi_event và multi_behavior.
[ ] Field số phải giữ đúng kiểu dữ liệu, không nhét text trạng thái vào field số.
[ ] Metadata AI/CV phải có source và confidence nếu áp dụng.
[ ] Khi không chắc chắn, dùng unknown/null hoặc yêu cầu HUMAN_CONFIRMED.
[ ] Chỉ dữ liệu VERIFIED mới dùng làm Ground Truth chính thức.
[ ] Không sửa hoặc ghi đè raw video.
[ ] Pipeline phải hỗ trợ resume và cache cho dữ liệu lớn.
```
