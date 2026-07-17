# Candidate Mining v1 — Vai trò B (Data & Automation)

> Mục tiêu: tạo evidence kỹ thuật để C review/gán nhãn. Pipeline không kết luận intrusion, ROI state, identity, loitering, ground truth hay KPI.

## 1. POC hiện tại: xem person detection

POC hiện tại chạy **Ultralytics RT-DETR-L pretrained COCO**, chỉ lọc COCO class `person`, trên GPU local. Đây là model COCO general-purpose, không phải model surveillance chuyên biệt.

Profile tạm thời:

```text
sample_fps = 5
image_size = 960
batch_size = 1
confidence_threshold = 0.20
```

Mỗi raw video chỉ có một JSON local bị Git-ignore, ghi đè cùng path khi chạy lại:

```text
data/raw/<video>.mp4
data/review_queue/person_detected/<raw-name>.detections.json
```

Không có MP4 review/debug, inventory hay manifest được tạo tự động trong POC viewer-first này. Sau khi operator chọn một logical span trong `browse`, họ có thể chọn **Export** để mở Windows Save As và xuất đúng context của span thành MP4 local; thao tác này không xảy ra khi chạy detector hoặc quét danh sách.

## 2. JSON bbox và viewer

JSON lưu evidence detector thật theo source frame: frame index, source timestamp, bbox pixel `[x1, y1, x2, y2]`, confidence và technical `track_id`/`episode_id`.

Detector chạy 5 FPS; viewer giữ nguyên snapshot bbox của sample gần nhất cho tới sample 5-FPS tiếp theo. Đây chỉ là cách hiển thị ổn định, không phải detector chạy 30 FPS, nội suy vị trí, prediction hay detection mới ở các frame giữa.

```powershell
# Tạo/cập nhật đúng một JSON cho raw video
.\.venv\Scripts\candidate-mining run "data\raw\<video>.mp4"

# Tool nội bộ quét toàn bộ raw videos A-Z, hiện bảng chọn
.\.venv\Scripts\candidate-mining browse

# Mở thẳng một raw video với JSON sẵn có
.\.venv\Scripts\candidate-mining inspect "data\raw\<video>.mp4"
```

Sau khi chọn raw → category → span trong `browse`, chọn `V` để xem hoặc `E` để export:

```text
V / view          Mở raw source, bbox overlay, chỉ trong context span
E / export clean  Mở Windows Save As và export clean H.264/AAC MP4 của context span
A / export bbox   Mở Windows Save As và export MP4 với bbox kỹ thuật đã lưu
B / back          Quay về danh sách span
```

Cả hai export dùng chính `context_start_sec`/`context_end_sec` đã lưu. `E` không render bbox; `A` render snapshot bbox kỹ thuật 5 FPS đã lưu và giữ box tới sample tiếp theo, nhưng vẫn chạy ở FPS nguồn và không gọi detector lại. Bbox MP4 là debug/review visualization, không phải ground truth hay nhãn event. Tool hỏi xác nhận nếu target đã tồn tại; Cancel Save As không tạo file. Export video camera là local sensitive artifact; không commit/push.

Viewer controls:

```text
Space       play/pause
Left/Right  step frame khi pause
[ / ]       seek ±5 giây
o           bật/tắt bbox
q / Esc     đóng viewer
```

`browse` quét video ở cả raw root và subfolder, sắp xếp A-Z theo relative path. Trạng thái:

- `READY`: JSON hợp lệ, có box.
- `EMPTY`: JSON hợp lệ, không có box.
- `MISSING`: chưa chạy detector cho video.
- `STALE`: JSON không khớp raw video hiện tại.
- `INVALID`: JSON hỏng/sai schema.

Với raw nằm trong subfolder, JSON giữ cấu trúc subfolder để không collision tên:

```text
data/raw/camera-a/segment.mp4
  -> data/review_queue/person_detected/camera-a/segment.detections.json
```

## 3. Candidate person cho handoff sau POC

Đơn vị candidate không phải từng người/technical episode. Một candidate là **một span thời gian liên tục có ít nhất một person** trong source video.

```text
candidate_start = first accepted person-positive sample
candidate_end   = last accepted person-positive sample
clip_start      = max(0, candidate_start - 5s)
clip_end        = min(video_duration, candidate_end + 5s)
```

- Các person đồng thời, `track_id`, hay `episode_id` khác nhau vẫn thuộc một source-level presence span nếu liên tục theo thời gian.
- `track_id`/`episode_id` chỉ là metadata debug, không phải identity và không tách candidate.
- Dùng `person_presence_merge_gap_seconds = 2.0`: gap giữa hai person-positive sample `<= 2s` nối cùng span; gap `> 2s` mở span mới.
- Span giữ toàn bộ thời lượng có person và chỉ thêm 5 giây ở hai biên ngoài.
- Không có folder/rule/threshold loitering. Role C chọn `event_start_sec`/`event_end_sec` cuối trong UI từ source-level span.

## 4. Future B → C handoff

Khi POC viewer ổn định, B có thể tái bật candidate-package output cho C/A. Contract tương lai dùng source-relative timestamps, logical sample ID và metadata candidate. C có quyền chọn/review event cuối trong UI; B không biến detection thành ground truth.

## 5. Local data policy

Không commit raw video hoặc generated artifacts trong:

```text
data/raw/
data/inventory/
data/manifests/
data/review_queue/
outputs/logs/
models/cache/
models/weights/
.cache/torch/
```

Video camera có thể chứa mặt, biển số hoặc thông tin vận hành. Weight phải được tải explicit vào `models/weights/`; normal run không được implicit download.
