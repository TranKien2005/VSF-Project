# VSF Project — AI Camera Test Data Preparation

Repository hỗ trợ chuẩn bị evidence kỹ thuật từ video camera để C review/gán nhãn. Model nghiệp vụ, ROI, KPI, ground truth, intrusion, authorization và loitering đều **ngoài phạm vi POC này**.

## Vai trò

| Vai trò | Phạm vi |
|---|---|
| A — QA / Test Design | use case, coverage, review bàn giao |
| B — Data & Automation | quét video, person detection, span kỹ thuật, tool xem |
| C — Annotation / Data Quality | UI chọn event interval, nhãn cuối, ground truth |

## POC hiện tại

POC dùng **Ultralytics RT-DETR-L pretrained COCO**, chỉ lọc COCO class `person`.

```text
sample_fps = 5
image_size = 960
batch_size = 1
confidence_threshold = 0.20
device = auto (RTX 4060 khi CUDA sẵn sàng)
```

RT-DETR-L là COCO general-object model, không phải model surveillance/perimeter chuyên biệt. Person detection là evidence kỹ thuật, không phải nhãn event thật.

### Raw input và output

Raw input đặt trong `data/raw/`; subfolder được hỗ trợ.

Mỗi raw video chỉ tạo **một JSON phụ trợ** trong category hiện dùng và ghi đè đúng path khi chạy lại:

```text
data/raw/front-gate.mp4
  -> data/review_queue/person_detected/front-gate.detections.json

data/raw/camera-a/segment.mp4
  -> data/review_queue/person_detected/camera-a/segment.detections.json
```

POC này không tự tạo inventory JSON, manifest CSV, proxy/subvideo MP4, review MP4 hay video debug. Raw video giữ nguyên; viewer đọc raw video và JSON để vẽ bbox trực tiếp. Operator có thể **chủ động export** một span đã chọn ra MP4 local qua Save As; đây không phải output tự động của pipeline.

## Chạy tool

### 1. Tạo virtual environment và cài dependencies

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[vision,dev]"
```

### 2. Tải RT-DETR-L local, chỉ một lần

```powershell
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l
```

Weights nằm tại `models/weights/rtdetr-l.pt`, bị Git-ignore. Normal run chỉ load file local; không tự tải model.

### 3. Chạy detection cho một raw video trực tiếp

```powershell
.\.venv\Scripts\candidate-mining run "data\raw\front-gate.mp4"
```

Lệnh chạy RT-DETR trên video được chọn, rồi ghi đè đúng JSON `person_detected` của video đó.

### 4. Chạy tool chọn một video hoặc tất cả video

```powershell
.\.venv\Scripts\candidate-mining run
```

Tool quét đệ quy toàn bộ `data/raw/`, sắp xếp relative path A–Z, sau đó hiện bảng:

```text
#   Raw video (alphabetical)
 1  camera-a/segment-001.mp4
 2  front-gate.mp4
Select number, A for all, or Q to quit:
```

- Nhập số: chỉ chạy raw video tương ứng.
- `A` / `all`: chạy tất cả video theo thứ tự bảng. Một video lỗi không làm dừng các video còn lại; cuối cùng tool báo số video thành công/tổng số.
- `Q` / `quit`: thoát, không chạy detection.

### 5. Xem evidence theo raw → category → logical span

```powershell
.\.venv\Scripts\candidate-mining browse
```

`browse` không chạy RT-DETR và không ghi file. Nó đi theo thứ tự:

```text
raw video
  → candidate category
    → logical source span
      → viewer raw video trong context của span
```

Ở POC hiện tại category duy nhất là `person_detected`. Sau khi chọn raw video và category, tool liệt kê các span:

```text
ID                    detected range       context range        max people  note
 1  person_detected-0001    0.0-41.8          0.0-42.0                 9  full source; context clipped
```

Sau khi chọn một span, tool hiện action menu:

```text
V / view          Mở raw video với bbox, seek tới context_start_sec và tự dừng tại context_end_sec
E / export clean  Mở Windows Save As để xuất clean source MP4 của context span
A / export bbox   Mở Windows Save As để xuất MP4 với bbox kỹ thuật đã lưu
B / back          Quay về danh sách span
```

`view` không ghi file. `E` dùng đúng `context_start_sec` / `context_end_sec` đã lưu trong JSON, xuất **clean source clip** (không burn-in bbox) bằng FFmpeg H.264/AAC MP4. `A` xuất cùng khoảng thời gian nhưng render bbox từ JSON và diagnostic header vào video; video chạy ở FPS nguồn, còn box vẫn giữ snapshot detector 5 FPS đến sample tiếp theo. `A` không chạy inference lại và bbox chỉ là technical detection, không phải ground truth/event label.

Cửa sổ Save As đề xuất tên dựa trên raw source, span ID và time range; bản bbox có hậu tố `_bbox`. Bấm Cancel thì không ghi file. Nếu target đã tồn tại, tool hỏi xác nhận overwrite trước khi chạy FFmpeg. Export bbox phải decode/render từng frame nên chậm hơn clean export; nếu source có audio thì audio gốc được giữ lại khi xuất.

Export luôn là thao tác thủ công, không tạo MP4 khi `run`, quét `browse`, hoặc chỉ chọn span. Video export có thể chứa dữ liệu camera nhạy cảm: chỉ lưu local và không commit/push. Nếu lưu bên trong repository, dùng một đường dẫn Git-ignore như `data/review_queue/`.

Viewer controls:

```text
Space       play/pause
Left/Right  step frame khi pause
[ / ]       seek ±5 giây
o           bật/tắt bbox
q / Esc     đóng viewer và quay lại span menu
```

### 6. Mở trực tiếp toàn raw video khi cần debug

```powershell
.\.venv\Scripts\candidate-mining inspect "data\raw\front-gate.mp4"
```

Lệnh này mở toàn raw source với JSON hiện có; nó hữu ích cho debug và vẫn không ghi file.

## Bbox 5 FPS và hiển thị

JSON chỉ lưu detection thật tại sample frame 5 FPS. Với video nguồn 30 FPS, detector thường chạy mỗi 6 frame. Viewer giữ snapshot bbox của sample gần nhất tới sample tiếp theo:

```text
frame sample 870 → vẽ box của sample 870
frame 871–875    → giữ box sample 870
frame sample 876 → thay bằng box sample 876
```

Đây là display policy để box không nhấp nháy. Nó không phải inference 30 FPS, nội suy vị trí hay motion prediction.

## Logical person span

Một logical `person_detected` span là đoạn thời gian liên tục có **ít nhất một person accepted detection**. Nó không tách theo từng người, `track_id`, hay `episode_id`.

```text
candidate_start = first accepted person-positive sample
candidate_end   = last accepted person-positive sample
context_start   = max(0, candidate_start - 5s)
context_end     = min(video_duration, candidate_end + 5s)
```

`person_presence_merge_gap_seconds = 2.0`:

- gap `<= 2s`: nối cùng presence span;
- gap `> 2s`: tạo span mới.

Nếu person-positive detections phủ liên tục từ đầu tới cuối raw source, một full-source span là kết quả đúng. Đây là trường hợp POC video hiện tại: span `0.0s → 41.8s`, context bị cắt ở hai đầu thành toàn bộ source ~42s. Không phải hệ thống chưa biết tách.

Technical `track_id`/`episode_id` chỉ lưu để debug; không phải identity và không tách span. Không có rule/folder/threshold loitering. C chọn final `event_start_sec` / `event_end_sec` trong UI từ logical source span.

## Kiểm tra kỹ thuật

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

## Git và dữ liệu nhạy cảm

Không commit/push raw video, generated JSON, model weights/cache hay runtime log. Các thư mục local nhạy cảm đã được Git-ignore:

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
Video camera có thể chứa mặt người, biển số hoặc thông tin vận hành. Chỉ commit code, schema, cấu hình không nhạy cảm, tài liệu và test fixture đã được phép sử dụng.

## Week 1 — Day 16 QA Artifacts

Artifact nghiệp vụ do A (QA Lead / Test Design) tạo ngày 16/07/2026, đặt tại `docs/week-1/day-16/`:

| Tài liệu | Nội dung |
|---|---|
| [Business_Clarification_Log_v0.1](docs/week-1/day-16/Business_Clarification_Log_v0.1.md) | 39 câu hỏi nghiệp vụ kèm status, owner trả lời, owner phê duyệt, deadline và impact |
| [AI_Testing_Objectives_v0.1](docs/week-1/day-16/AI_Testing_Objectives_v0.1.md) | Mục tiêu kiểm thử, KPI dự kiến, phạm vi và ngoài phạm vi |
| [Use_Case_Catalogue_v0.1](docs/week-1/day-16/Use_Case_Catalogue_v0.1.md) | Use case intrusion, camera cover/tamper, camera movement và E2E |
| [Assumption_and_Blocker_Log_v0.1](docs/week-1/day-16/Assumption_and_Blocker_Log_v0.1.md) | 7 assumption và 9 blocker kèm fallback |
| [Requirement_Traceability_Matrix_v0.1](docs/week-1/day-16/Requirement_Traceability_Matrix_v0.1.md) | Truy vết Requirement → Use case → Test category → Evidence → KPI |
| [Kickoff_Meeting_Minutes_2026-07-16](docs/week-1/day-16/Kickoff_Meeting_Minutes_2026-07-16.md) | Biên bản kickoff, quyết định, blocker và action item |

Tại thời điểm phát hành, **chưa có câu hỏi nghiệp vụ nào ở trạng thái `Answered`**. Mọi điểm chưa rõ được ghi là `Open`, `Assumption` hoặc `Blocked`; không suy diễn câu trả lời. KPI và acceptance criteria được khóa vào ngày 17/07/2026.

## Week 1 — Day 17 QA Artifacts

Artifact chiến lược kiểm thử và KPI do A tạo ngày 17/07/2026, đặt tại `docs/week-1/day-17/`:

| Tài liệu | Nội dung |
|---|---|
| [Acceptance_Criteria_v1.0](docs/week-1/day-17/Acceptance_Criteria_v1.0.md) | Điều kiện đạt cho intrusion, cover, movement, data quality và E2E; điều kiện loại khỏi KPI |
| [Alert_Severity_and_Event_Rule_Spec_v1.0](docs/week-1/day-17/Alert_Severity_and_Event_Rule_Spec_v1.0.md) | Cấp 1–4, event boundary, state transition, dedup/cooldown, uncertain case |
| [Metric_and_KPI_Calculation_Rule_v1.0](docs/week-1/day-17/Metric_and_KPI_Calculation_Rule_v1.0.md) | Đơn vị tính theo event, matching rule, TP/FP/FN/TN, duplicate, misclassification, exclusion |
| [Requirement_Traceability_Matrix_v1.0](docs/week-1/day-17/Requirement_Traceability_Matrix_v1.0.md) | 30 requirement truy vết Requirement → Use case → Test category → Evidence → KPI |
| [Risk_and_Dependency_Log_v1.0](docs/week-1/day-17/Risk_and_Dependency_Log_v1.0.md) | 21 risk và 6 dependency kèm mitigation/fallback; đánh giá gate Tuần 1 |
| [Coverage_Quota_v1.0.csv](docs/week-1/day-17/Coverage_Quota_v1.0.csv) | 38 slice quota theo camera, ngày/đêm, event, quality condition, positive/negative/hard negative |

Lưu ý khi đọc:

- **Các tài liệu đánh số `v1.0` theo tên artifact quy định trong kế hoạch nhưng chưa được khóa.** Chưa có câu hỏi nghiệp vụ nào từ ngày 16 được stakeholder trả lời, nên mọi điểm phụ thuộc severity, event boundary, cover/movement threshold, dedup và latency đều mang trạng thái `TBD_STAKEHOLDER_APPROVAL` hoặc `ASSUMPTION`.
- KPI tính theo **event**, không theo frame. Ghi chú bắt buộc: `FP/(TP+FP)` **bằng `1 − Precision`**, không phải false-positive rate thống kê `FP/(FP+TN)`.
- `Coverage_Quota_v1.0.csv` là **sampling hypothesis**: `target_count` và `camera_group=all` là giá trị khởi điểm, sẽ điều chỉnh sau khi có video inventory ở Tuần 2.
- Gate Tuần 1 hiện **chưa đủ điều kiện mở** — xem mục 4 của Risk and Dependency Log.

## Bước tiếp theo

1. B: chạy `candidate-mining run` cho raw video local và review logical span qua `candidate-mining browse`.
2. C: hoàn thiện annotation UI để chọn final event interval trong logical source span; JSON detection không phải ground truth.
3. A: review coverage, artifact và checklist bàn giao.

Các tài liệu Week 1 ở trên là artifact QA/kế hoạch độc lập. Chúng không thay đổi scope kỹ thuật của POC person-detection hiện tại.
