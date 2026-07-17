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

## Week 1 — Day 16 A / QA-Test Design Artifacts

Ngày 16 chỉ tạo tài liệu planning/specification; chưa có raw video/data thật, inventory, candidate result, annotation, ground truth, coverage hay KPI result. Các artifact của A đặt tại `docs/week-1/day-16/`:

| Tài liệu | Nội dung |
|---|---|
| [AI_Testing_Objectives_v0.1](docs/week-1/day-16/AI_Testing_Objectives_v0.1.md) | Mục tiêu, scope, ngoài phạm vi và KPI event-level target; phân biệt candidate evidence với evaluation cuối. |
| [Use_Case_Catalogue_v0.1](docs/week-1/day-16/Use_Case_Catalogue_v0.1.md) | Scenario ROI Green/Yellow/Red, cover, movement, interference và data/E2E boundary. |
| [Metric_and_KPI_Calculation_Rule_v0.1](docs/week-1/day-16/Metric_and_KPI_Calculation_Rule_v0.1.md) | TP/FP/FN/TN, matching, duplicate, misclassification, exclusion và `Chưa kết luận`. |
| [Acceptance_Criteria_Draft_v0.1](docs/week-1/day-16/Acceptance_Criteria_Draft_v0.1.md) | Draft pass/fail theo category/evidence và dependency cần cho execution. |

## Week 1 — Day 17 A / QA-Test Design Artifacts

Ngày 17 hoàn thiện plan cho execution Tuần 2–3. `v1.0` là version artifact theo kế hoạch, không phải tuyên bố đã có data-result hoặc tài liệu đã được phê duyệt/khóa.

| Tài liệu | Nội dung |
|---|---|
| [Acceptance_Criteria_v1.0](docs/week-1/day-17/Acceptance_Criteria_v1.0.md) | Acceptance theo intrusion, cover, movement, traceability và E2E; điều kiện loại/KPI conclusion. |
| [Requirement_Traceability_Matrix_v1.0](docs/week-1/day-17/Requirement_Traceability_Matrix_v1.0.md) | Requirement → scenario → evidence → acceptance → KPI/output boundary. |
| [Coverage_Quota_v1.0.csv](docs/week-1/day-17/Coverage_Quota_v1.0.csv) | Sampling hypothesis theo scenario/condition; `target_count` không phải sample có sẵn hay coverage đã đạt. |
| [Risk_and_Dependency_Log_v1.0](docs/week-1/day-17/Risk_and_Dependency_Log_v1.0.md) | Dependency thực tế từ data/system access và limitation handling, không có deadline/approval giả. |
| [Three_Week_Execution_Matrix_v1.0](docs/week-1/day-17/Three_Week_Execution_Matrix_v1.0.md) | Phân bổ A/B/C theo ba tuần, exit evidence và gate discipline. |

## Week 1 — Day 16 B / Data & Automation Artifacts

Các tài liệu ngày 16 mô tả code POC hiện có và design chuẩn bị nhận data; không có raw-data execution hay generated artifact thực tế.

| Tài liệu | Nội dung |
|---|---|
| [Dataset_Folder_and_Manifest_Design_v0.1](docs/week-1/day-16/Dataset_Folder_and_Manifest_Design_v0.1.md) | Folder/manifest contract: JSON person hiện tại so với candidate manifest dự kiến. |
| [Candidate_Mining_Pseudocode_v0.1](docs/week-1/day-16/Candidate_Mining_Pseudocode_v0.1.md) | Pseudocode POC person-only thực tế và target flow chưa implement. |
| [Technical_Readiness_Checklist_v0.1](docs/week-1/day-16/Technical_Readiness_Checklist_v0.1.md) | Python/model/GPU/FFmpeg/raw access/storage readiness checklist. |
| [Camera_Stream_and_ROI_Evidence_Checklist_v0.1](docs/week-1/day-16/Camera_Stream_and_ROI_Evidence_Checklist_v0.1.md) | Stream/camera/ROI/system evidence cần nhận từ Tuần 2. |
| [KPI_Calculation_Sheet_Template_v0.1](docs/week-1/day-16/KPI_Calculation_Sheet_Template_v0.1.md) | Template event-level KPI; runtime hiện không tính KPI. |

## Week 1 — Day 17 B / Data & Automation Artifacts

Các tài liệu ngày 17 là architecture, runbook, policy và contract cho execution Tuần 2–3. Những workflow chưa được code hiện tại hỗ trợ được ghi rõ là planned/not implemented.

| Tài liệu | Nội dung |
|---|---|
| [Data_Pipeline_Architecture_v1.0](docs/week-1/day-17/Data_Pipeline_Architecture_v1.0.md) | Tách current person-JSON POC lane khỏi target pipeline. |
| [Data_Receipt_and_Inventory_Runbook_v1.0](docs/week-1/day-17/Data_Receipt_and_Inventory_Runbook_v1.0.md) | Intake/checksum/inventory procedure; inventory helpers chưa là CLI workflow. |
| [Leakage_and_Source_Group_Policy_v1.0](docs/week-1/day-17/Leakage_and_Source_Group_Policy_v1.0.md) | Source-group/split policy và eligibility state. |
| [Candidate_and_Evidence_Data_Contract_v1.0](docs/week-1/day-17/Candidate_and_Evidence_Data_Contract_v1.0.md) | Current `person-detections.v1` contract và candidate/review contract dự kiến. |
| [Local_Artifact_and_Git_Policy_v1.0](docs/week-1/day-17/Local_Artifact_and_Git_Policy_v1.0.md) | Local sensitive-artifact, hashing, access và Git boundary policy. |

## Week 1 — Day 16 C / Annotation & Data Quality Artifacts

C sử dụng hướng **internal UI** nhưng UI này chưa được implement trong repository. Review unit là logical source span và final event interval luôn là thời gian tính từ đầu raw source. Annotation được thiết kế là extension của cùng JSON `person-detections.v1` theo source; không tạo standalone annotation format/file.

| Tài liệu | Nội dung |
|---|---|
| [Label_Taxonomy_v0.1](docs/week-1/day-16/Label_Taxonomy_v0.1.md) | Nhãn review, interference, review status và ranh giới severity. |
| [Metadata_Schema_v0.1](docs/week-1/day-16/Metadata_Schema_v0.1.md) | Current JSON fields và annotation extension proposal chưa được code hỗ trợ. |
| [Labeling_Guideline_v0.1](docs/week-1/day-16/Labeling_Guideline_v0.1.md) | Quy trình source-relative review trên future internal UI. |
| [Annotation_Queue_Entry_Template_v0.1](docs/week-1/day-16/Annotation_Queue_Entry_Template_v0.1.md) | Template queue entry theo source/SHA/span/context/final event. |
| [Disagreement_and_Adjudication_Process_v0.1](docs/week-1/day-16/Disagreement_and_Adjudication_Process_v0.1.md) | Second review, adjudication, escalation và unresolved exclusion. |

## Week 1 — Day 17 C / Annotation & Data Quality Artifacts

Các tài liệu này chuẩn bị QC/release workflow từ Tuần 2–3; không tuyên bố có annotation, calibration, agreement hoặc ground truth result. Agreement threshold chưa được quyết định và được ghi là `TBD_STAKEHOLDER_APPROVAL`.

| Tài liệu | Nội dung |
|---|---|
| [Labeling_Guideline_v0.2](docs/week-1/day-17/Labeling_Guideline_v0.2.md) | Guideline operational: internal UI planned, source-relative event interval và output extension. |
| [Annotation_QC_Protocol_v1.0](docs/week-1/day-17/Annotation_QC_Protocol_v1.0.md) | Schema/source/span/label/reviewer/ROI/release validation. |
| [Calibration_Plan_v1.0](docs/week-1/day-17/Calibration_Plan_v1.0.md) | Kế hoạch calibration future, không có calibration result. |
| [Annotation_Agreement_Plan_v1.0](docs/week-1/day-17/Annotation_Agreement_Plan_v1.0.md) | Double-review, Kappa/boundary measurement và threshold TBD. |
| [Ground_Truth_Release_Criteria_v1.0](docs/week-1/day-17/Ground_Truth_Release_Criteria_v1.0.md) | Điều kiện ground truth/golden/diagnostic/exclusion release. |

Fact mentor được phản ánh trong các artifact: ROI Green/Yellow/Red; cover positive khi ≥30% trong ≥120 giây; movement positive là strong shake hoặc rotation/changed orientation; rain, vehicle glare và scene motion không do camera là interference; severity do rule engine quyết định. Reviewer không gán Cấp 1–4.

KPI tính theo **event**, không theo frame. `FP/(TP+FP)` bằng `1 − Precision`, không phải false-positive rate thống kê `FP/(FP+TN)`. Coverage, ground truth và KPI chỉ được kết luận sau khi có data/evidence thực tế từ Tuần 2–3.

## Bước tiếp theo

1. Tuần 2 khi nhận raw data: B chạy `candidate-mining run` và review technical person span qua `candidate-mining browse` theo capability thực tế.
2. C xây dựng future internal UI để đọc/extend JSON theo source, review source-relative span và ghi final event interval; JSON detection không phải ground truth.
3. A áp dụng coverage hypothesis, acceptance, traceability và risk/dependency plan; KPI chỉ kết luận khi đủ evidence và matching rule.

Các tài liệu Week 1 ở trên là artifact QA/kế hoạch độc lập. Chúng không thay đổi scope kỹ thuật của POC person-detection hiện tại.
