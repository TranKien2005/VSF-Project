# Kế hoạch 03 tuần xây dựng Test Data & Ground Truth — AI Camera An ninh Vành đai

> **Phiên bản:** v1.0  
> **Mục tiêu:** tạo bộ dữ liệu kiểm thử có thể truy vết, ground truth được kiểm soát chất lượng và golden set v1 cho ba bài toán: **trèo rào/xâm nhập**, **che camera**, **rung lắc hoặc xoay lệch camera**.

---

## 1. Thông tin đầu vào đã biết

| Hạng mục | Thông tin |
|---|---|
| Hãng camera | HIKVISION |
| Model | `DS-2CD3T46G2-ISU/SL` |
| Serial tham chiếu | `DS-2CD3T46G2-ISU/SL20241229AAWRFV0827781` |
| Firmware | `V5.7.55` |
| Khoảng cách camera | Khoảng 40 m giữa các camera |
| ROI | Đã có sẵn: người dùng vẽ ROI Xanh/Vàng/Đỏ trên ảnh camera; tool lưu cấu hình để xử lý video |

### 1.1. Nguyên tắc về ROI

Việc **vẽ, tạo hoặc thay đổi ROI không nằm trong phạm vi** kế hoạch này. Khi kiểm thử và gán nhãn, nhóm chỉ cần lưu bằng chứng cấu hình đang áp dụng:

- `camera_id`;
- `roi_config_id` hoặc `roi_version`;
- thời điểm ROI có hiệu lực;
- ảnh snapshot hoặc đường dẫn tham chiếu ROI;
- vùng ROI mà đối tượng/sự kiện liên quan.

Điều này giúp giải thích đúng/sai khi một cảnh báo phụ thuộc vị trí ROI, đồng thời tránh việc test nhầm giữa các phiên bản ROI.

---

## 2. Mục tiêu, phạm vi và kết quả kỳ vọng

### 2.1. Mục tiêu trong 03 tuần

1. Khóa định nghĩa nghiệp vụ, test scope, quy tắc tính KPI và tiêu chí pass/fail.
2. Kiểm kê raw video, kiểm tra tính truy vết, trùng lặp và nguy cơ data leakage.
3. Tạo candidate clip bằng pipeline bán tự động; **không dùng output của tool làm ground truth tự động**.
4. Lấy mẫu có kiểm soát và gán nhãn bởi con người.
5. Tạo ground truth v1.0, manifest được version hóa, báo cáo coverage và golden set nhỏ có chất lượng cao.
6. Có đủ bằng chứng để tính KPI riêng cho ba nhóm kịch bản.

### 2.2. Phạm vi bắt buộc

| Nhóm | Nội dung |
|---|---|
| Trèo rào/xâm nhập | Lảng vảng ngoài hàng rào; tiếp cận sát rào; trèo/chạm đỉnh rào; đi vào khu cấm theo ROI |
| Che camera | Che ngắn hạn/dài hạn; che một phần/toàn phần; phân biệt với mưa, chói sáng và các nhiễu môi trường |
| Camera movement | Rung mạnh; xoay/lệch hướng duy trì; phân biệt với rung ngắn do môi trường |
| Data quality | Inventory, duplicate, leakage, annotation, agreement, ground truth, dataset versioning |
| E2E tối thiểu | Cảnh báo có đúng camera, timestamp, loại sự kiện/cấp độ và bằng chứng clip/log; không bị alert trùng không kiểm soát |

### 2.3. Ngoài phạm vi bản v1

Các hạng mục sau ghi nhận là phase mở rộng nếu có thêm thời gian/dữ liệu:

- stress/load test quy mô lớn hoặc nhiều camera đồng thời;
- fairness chuyên sâu theo nhóm nhân khẩu học;
- multi-camera tracking/nhận dạng cùng đối tượng qua nhiều camera;
- tạo synthetic data ở quy mô lớn;
- kiểm thử an ninh mạng thiết bị, hardening hoặc pentest;
- thay đổi model, firmware hoặc cấu hình ROI production.

---

## 3. KPI, confusion matrix và quy tắc tính

### 3.1. KPI đã được chốt

| Mã KPI | Chỉ số | Nhóm kịch bản | Ngưỡng đạt |
|---|---|---|---:|
| M1 | Recall — tỷ lệ phát hiện | Trèo rào | ≥ 90% |
| M2 | Tỷ lệ báo động giả | Trèo rào | ≤ 10% |
| M3 | Precision — độ chính xác | Trèo rào | ≥ 90% |
| M1 | Recall — tỷ lệ phát hiện | Xoay camera | ≥ 90% |
| M2 | Tỷ lệ báo động giả | Xoay camera | ≤ 10% |
| M3 | Precision — độ chính xác | Xoay camera | ≥ 90% |
| M1 | Recall — tỷ lệ phát hiện | Che camera | ≥ 90% |
| M2 | Tỷ lệ báo động giả | Che camera | ≤ 10% |
| M3 | Precision — độ chính xác | Che camera | ≥ 90% |

### 3.2. Định nghĩa kết quả

| Ký hiệu | Định nghĩa |
|---|---|
| TP — Báo đúng | Có ground-truth event và hệ thống báo đúng loại sự kiện trong cửa sổ thời gian đã thống nhất |
| FP — Báo sai | Hệ thống báo nhưng không có event tương ứng, hoặc báo sai loại sự kiện theo quy tắc mapping đã khóa |
| FN — Không báo | Có ground-truth event nhưng hệ thống không báo trong cửa sổ thời gian cho phép |
| TN — Bỏ qua đúng | Không có event và hệ thống không báo |

### 3.3. Công thức

```text
Precision          = TP / (TP + FP)
Recall             = TP / (TP + FN)
Tỷ lệ báo động giả = FP / (TP + FP)
```

> **Lưu ý quan trọng:** theo công thức được giao, `FP/(TP+FP) = 1 - Precision`. Vì vậy M2 và M3 là hai cách nhìn cùng một mẫu số. Kế hoạch vẫn báo cáo cả hai đúng theo KPI, nhưng **Tuần 1 cần xác nhận tên gọi hiển thị chính thức** để không nhầm với false-positive rate thống kê `FP/(FP+TN)`.

### 3.4. Quy tắc tính bắt buộc phải khóa trong Tuần 1

- Tính theo **event**, không tính theo từng frame.
- Một ground-truth event và nhiều alert trùng chỉ được tính **một TP**; các alert còn lại được ghi nhận là `duplicate_alert` để báo cáo bổ sung.
- Alert sai loại nhưng cùng khoảng thời gian được quy về FP/FN hay `misclassification` phải được thống nhất trước khi tính KPI.
- `ambiguous` và `invalid` không được dùng để tính KPI chính thức.
- Case rerun phải giữ `sample_id`/`run_id`; chỉ kết quả đã được review và khóa mới được đưa vào bảng KPI.

---

## 4. Định nghĩa kịch bản và taxonomy nhãn

### 4.1. Trèo rào/xâm nhập

| Nhãn sự kiện | Diễn giải | ROI/cấp độ mong đợi |
|---|---|---|
| `person_near_fence` | Đối tượng lảng vảng ở vùng ngoài hàng rào | ROI Xanh; Cấp 4 theo dõi, tối đa 5 phút theo rule nghiệp vụ |
| `person_approaching_fence` | Đối tượng tiếp cận sát hàng rào | ROI Vàng; Cấp 2 hoặc 3 — cần chốt rule phân biệt |
| `person_touching_fence` | Đối tượng chạm/bám hàng rào | ROI Vàng/Đỏ tùy ROI thực tế |
| `person_climbing_fence` | Đối tượng có hành vi trèo rào | Cấp độ cần chốt theo event boundary |
| `person_on_fence_top` | Đối tượng ở đỉnh hàng rào | Thông thường ứng viên Cấp 1; cần chốt |
| `person_crossing_fence` | Đối tượng vượt qua hàng rào | ROI Đỏ; Cấp 1 khẩn cấp |
| `person_inside_restricted_area` | Đối tượng ở trong khu cấm | ROI Đỏ; Cấp 1 khẩn cấp |
| `person_outside_roi` | Có người nhưng ngoài vùng cảnh báo | Negative/hard negative |

### 4.2. Che camera/tamper và nhiễu liên quan

| Nhãn | Vai trò dự kiến |
|---|---|
| `lens_full_cover` | Positive: che gần/toàn bộ lens |
| `lens_partial_cover` | Positive/edge: che một phần, cần ngưỡng che và thời lượng |
| `temporary_occlusion` | Edge/negative tùy rule: vật thể che tạm thời |
| `rain_heavy`, `water_drop_or_fog` | Environmental hard negative hoặc camera-health riêng |
| `headlight_glare` | Hard negative: ánh đèn xe quét qua |
| `low_light` | Quality condition/hard negative |
| `black_screen`, `video_freeze`, `video_loss` | Camera health riêng hay tamper: cần chốt |

### 4.3. Rung lắc/xoay camera

| Nhãn | Diễn giải |
|---|---|
| `temporary_shake` | Rung ngắn rồi trở lại bình thường |
| `environmental_vibration` | Rung do gió, xe, cổng hoặc điều kiện ngoài ý muốn |
| `sustained_camera_displacement` | Camera lệch/xoay hướng duy trì; positive chính |
| `roi_drift` | Góc camera lệch làm ROI không còn bám đúng vùng vật lý |
| `scene_change_non_camera_move` | Cảnh thay đổi nhưng camera không bị dịch chuyển; hard negative |

### 4.4. Trạng thái annotation chung

```text
confirmed_positive
confirmed_negative
needs_second_review
ambiguous
invalid
```

`ambiguous` và `invalid` được lưu trong dataset để cải thiện guideline, nhưng **không đưa vào golden set** và không tính KPI chính thức.

---

## 5. Phân vai tổng thể và RACI

### 5.1. Trách nhiệm chính

| Vai trò | Người | Trách nhiệm |
|---|---|---|
| A — QA Lead / Test Design | A | Chốt yêu cầu, use case, metric, pass/fail; quản lý traceability, coverage, rủi ro, tiến độ, triage và bàn giao |
| B — Data & Automation | B | Inventory, metadata, kiểm tra video, leakage, mining, sampling, proxy clip, manifest, validation, versioning và báo cáo phân phối |
| C — Annotation & Data Quality | C | Taxonomy/guideline, calibration, human review, event boundary, nhãn kép, agreement, disagreement, ground truth, golden set |

### 5.2. RACI rút gọn

| Công việc | A | B | C |
|---|---:|---:|---:|
| Mục tiêu, phạm vi, use case, pass/fail | A/R | C | C |
| KPI definition và quy tắc tính event | A/R | C | C |
| Inventory và kiểm tra kỹ thuật video | C | A/R | I |
| Data leakage và split manifest | C | A/R | C |
| Candidate mining/pipeline/proxy clip | C | A/R | C |
| Sampling strategy và quota coverage | A/R | R | C |
| Label taxonomy/guideline | C | C | A/R |
| Annotation vòng 1 | R | R | A/R |
| Agreement/disagreement/ground truth | C | C | A/R |
| Schema validation/version/manifest | C | A/R | C |
| Coverage/report/handover | A/R | R | R |

**Nguyên tắc review:** người tạo artifact không là người duy nhất phê duyệt artifact đó. A và B tham gia annotation theo quota để tạo review chéo; C điều phối chất lượng nhãn.

---

## 6. Câu hỏi phải chốt trong Tuần 1

Đúng: **câu hỏi cần hỏi mentor/stakeholder chủ yếu phải được đưa vào Tuần 1**. Nếu chờ tới Tuần 2 hoặc 3, nhóm có thể làm sai dataset, nhãn hoặc cách tính KPI. Các câu hỏi dưới đây được chia cho từng người để có owner rõ ràng.

| Phần cần chốt | Câu hỏi | Owner hỏi/ghi nhận | Phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|
| Object scope | Chỉ phát hiện người, hay gồm xe/động vật/nhân viên? Có whitelist không? | A | Stakeholder/AI Lead | Ngày 16 | Không phân loại được TP/FP đúng |
| ROI evidence | Tool cung cấp `roi_config_id`, phiên bản, snapshot và thời điểm hiệu lực thế nào? | B | Product/Technical Owner | Ngày 16 | Không truy vết được cảnh báo theo ROI; **không hỏi tạo ROI mới** |
| Cấp 2 và Cấp 3 | ROI Vàng phân biệt Cấp 2/Cấp 3 dựa trên thời lượng, vị trí hay hành vi nào? | A | Stakeholder | Ngày 16 | Không gán severity nhất quán |
| Event boundary | Khi nào event bắt đầu/kết thúc? Người chỉ đưa tay vào ROI đỏ hoặc trèo rồi quay xuống có tính Cấp 1 không? | A + C | Stakeholder | Ngày 16 | FN/TP và nhãn boundary sai |
| Chuyển cấp/dedup | Xanh → Vàng → Đỏ là một incident cập nhật hay nhiều alert? Cooldown là bao lâu? | A | Product/Operations Owner | Ngày 17 | Không tính được duplicate alert/KPI event |
| Cover/tamper | Che bao nhiêu % và bao lâu là alert? Mưa lớn/chói đèn/mất hình/freeze được tính tamper hay camera health? | A + C | Stakeholder/AI Lead | Ngày 16 | Positive/negative bị lẫn |
| Camera movement | Rung/xoay lệch bao nhiêu pixel/độ/thời lượng là positive? Rung rồi trở lại có báo không? | B + C | AI Lead/Technical Owner | Ngày 16 | Không dựng được test boundary |
| KPI denominator | TP/FP/FN tính theo event như thế nào? Alert sai loại tính FP+FN hay misclassification? Tên M2 có giữ là “tỷ lệ báo động giả” không? | A + B | Stakeholder/QA Lead | Ngày 17 | Không thể kết luận KPI nhất quán |
| Latency/SLA | Cửa sổ phát hiện cho Cấp 1/cover/movement và mốc tính latency là gì? | A + B | Product/Operations Owner | Ngày 17 | Không đánh giá E2E được |
| Data/train leakage | AI team có train manifest, checksum, source list hoặc danh sách camera/ngày train không? | B | AI Team | Ngày 16 | Chỉ ghi nhận test eligibility `Unknown`, không chứng nhận độc lập |
| Ground truth | Ai quan sát hiện trường, nguồn nào là chuẩn; ai adjudicate case bất đồng? | C | Stakeholder | Ngày 17 | Không khóa được nhãn cuối |
| PII/storage | Chính sách lưu video/mặt/biển số, quyền truy cập và thời hạn lưu là gì? | B + C | Security/Data Owner | Ngày 17 | Rủi ro tuân thủ và bàn giao |

---

## 7. Kế hoạch chi tiết theo tuần và từng người

## Tuần 1 — Nắm bài toán, chốt rule và lập kế hoạch

> **Mục tiêu tuần:** khóa đủ requirement để không tạo dataset sai; có scope v1, KPI rule, guideline nháp, data-access plan và owner phê duyệt.

### Ngày 16 — Kickoff, làm rõ nghiệp vụ và khảo sát readiness

#### A — QA Lead / Test Design

1. Chủ trì kickoff với AI team, stakeholder và vận hành.
2. Trình bày ba phạm vi bắt buộc: intrusion, camera cover/tamper, camera movement.
3. Hỏi và ghi nhận toàn bộ câu hỏi nghiệp vụ thuộc các dòng Object scope, Cấp 2/3, Event boundary, Dedup, Cover/tamper, KPI và SLA trong [Mục 6](#6-câu-hỏi-phải-chốt-trong-tuần-1).
4. Lập `Business_Clarification_Log_v0.1`, mỗi câu có trạng thái `Open/Answered/Assumption/Blocked`.
5. Tạo traceability ban đầu: Requirement → Use case → Test category → Evidence → KPI.

**Đầu ra:**

- `Business_Clarification_Log_v0.1`
- `AI_Testing_Objectives_v0.1`
- `Use_Case_Catalogue_v0.1`
- danh sách assumption và blocker.

#### B — Data & Automation

1. Xác minh quyền truy cập raw video, camera/log/API, storage và danh sách nguồn data.
2. Thu thập stream profile thực tế: resolution, FPS, codec, bitrate, timestamp, NTP/timezone, source ID.
3. Xác nhận cách lấy `roi_config_id`, `roi_version`, snapshot ROI; **không cấu hình hoặc thay đổi ROI**.
4. Lập checklist công cụ: Python, FFmpeg/ffprobe, OpenCV, detector nhỏ nếu được chấp thuận, Label Studio/CVAT, Git, DVC/manifest.
5. Hỏi AI team về train-data manifest và các giới hạn môi trường chạy.

**Đầu ra:**

- `Technical_Readiness_Checklist_v0.1`
- `Camera_Stream_and_ROI_Evidence_Checklist_v0.1`
- `Data_Pipeline_Architecture_v0.1`
- `Dependency_and_Access_Log_v0.1`.

#### C — Annotation & Data Quality

1. Tạo taxonomy nhãn v0.1 theo [Mục 4](#4-định-nghĩa-kịch-bản-và-taxonomy-nhãn).
2. Soạn metadata schema nháp và trạng thái review.
3. Chuẩn bị câu hỏi về event start/end, case ambiguous, ground truth source, adjudicator, PII.
4. Khảo sát Label Studio/CVAT/công cụ nội bộ theo tiêu chí: hỗ trợ video, time segment, reviewer thứ hai, export metadata.

**Đầu ra:**

- `Label_Taxonomy_v0.1`
- `Metadata_Schema_v0.1`
- `Annotation_Tool_Proposal`
- `Labeling_Guideline_v0.1`.

### Ngày 17 — Khóa strategy, metric và lịch triển khai

#### Công việc chung buổi sáng

1. Review câu trả lời từ mentor/stakeholder; đánh dấu các điểm chỉ là assumption.
2. Chốt phạm vi MVP và các hạng mục out-of-scope.
3. Khóa quy tắc event-level KPI, mapping alert, duplicate và uncertain/invalid.
4. Chốt owner phê duyệt pass/fail; chốt DoD của từng tuần.
5. Nếu có blocker chưa giải quyết, ghi rõ impact và phương án fallback, không tự diễn giải requirement.

#### A — QA Lead / Test Design

1. Hoàn thiện use case, test taxonomy, risk priority và acceptance criteria theo KPI đã chốt.
2. Tạo `Alert_Severity_and_Event_Rule_Spec_v1.0`: Cấp 1–4, state transition, cooldown/dedup, event boundary.
3. Xây dựng quota coverage theo camera, ngày/đêm, quality condition, event type, negative/adversarial.
4. Chốt RACI, weekly schedule và requirement traceability matrix.

**Đầu ra:**

- `Acceptance_Criteria_v1.0`
- `Alert_Severity_and_Event_Rule_Spec_v1.0`
- `Metric_and_KPI_Calculation_Rule_v1.0`
- `Requirement_Traceability_Matrix_v1.0`
- `Risk_and_Dependency_Log_v1.0`.

#### B — Data & Automation

1. Hoàn thiện thiết kế folder, manifest và pipeline candidate mining.
2. Xác định quy tắc kiểm tra file hỏng, checksum, duplicate, time drift và source-group split.
3. Thiết kế bảng KPI input gồm event ID, alert ID, outcome TP/FP/FN/TN, reviewer, evidence link.
4. Chạy dry run tối thiểu một case mỗi nhóm: intrusion, cover, movement; xác minh thu được video, timestamp, ROI version, alert/log.

**Đầu ra:**

- `Dataset_Folder_and_Manifest_Design_v1.0`
- `Candidate_Mining_Pseudocode_v1.0`
- `KPI_Calculation_Sheet_Template`
- `Dry_Run_Evidence_Report`.

#### C — Annotation & Data Quality

1. Hoàn thiện guideline v0.2 từ câu trả lời đã chốt.
2. Xác định quy trình blind review, second review và adjudication.
3. Chuẩn bị tập calibration 30–50 clip hoặc số lượng phù hợp nguồn data.
4. Chốt rule nhãn cho partial cover, mưa/chói, shake vs displacement, person outside ROI và multiple events.

**Đầu ra:**

- `Labeling_Guideline_v0.2`
- `Calibration_Plan`
- `Disagreement_and_Adjudication_Process`
- `Annotation_Queue_Entry_Template`.

### Gate kết thúc Tuần 1

Chỉ chuyển Tuần 2 khi:

- [ ] Có owner phê duyệt scope/pass-fail hoặc assumption đã được chấp nhận.
- [ ] Cấp 2/Cấp 3, Cấp 1 boundary, cover/tamper và movement boundary có định nghĩa đủ để gán nhãn.
- [ ] KPI được chốt theo event và cách đếm TP/FP/FN rõ ràng.
- [ ] Biết data source, quyền truy cập, metadata tối thiểu và cách tham chiếu ROI version.
- [ ] Chọn được tool/phương án review.
- [ ] Dry run tạo được evidence đầy đủ cho ít nhất một case mỗi nhóm.

---

## Tuần 2 — Raw video đến candidate annotation queue

> **Mục tiêu tuần:** inventory dữ liệu, bảo vệ khỏi leakage, tạo candidate clip có thể truy vết, sampling có kiểm soát và hàng đợi review. **Chưa tuyên bố đây là ground truth cuối.**

### Ngày 1 — Nhận và kiểm kê dữ liệu

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Đối chiếu dữ liệu nhận được với use case/quota; cập nhật traceability và ưu tiên thiếu hụt | `Data_Receipt_vs_Usecase_Check` |
| B | Quét video bằng ffprobe/script: duration, FPS, resolution, codec, lỗi file, camera/source ID, timestamp, ROI reference, checksum | `video_inventory.csv`, `invalid_video_report.csv`, `duplicate_video_report.csv` |
| C | Xem mẫu mỗi camera/bối cảnh; xác minh ngày/đêm, timestamp, góc nhìn và vấn đề nhãn | `Initial_Data_Observation_Report`, guideline cập nhật |

### Ngày 2 — Phân tầng, split và leakage

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Khóa slice bắt buộc: camera, location, ngày/đêm, near/mid/far, lighting, event, video quality | `Coverage_Slice_Definition` |
| B | Gắn source-group ID theo camera/ngày/video nguồn; đối chiếu train list; gắn `Train overlap/Suspected/Test eligible/Unknown`; tạo phân phối sơ bộ | `data_split_manifest_v0.1`, `data_leakage_check_report`, `data_distribution_report_v0.1` |
| C | Kiểm tra thủ công clip nghi trùng/giống nhau; xác nhận rule sample độc lập | `Manual_Overlap_Review_Log` |

> Nếu AI team chưa cung cấp train manifest: trạng thái phải là `Unknown`; không được tuyên bố test set độc lập với train data.

### Ngày 3 — Xây candidate mining pipeline

#### B — Owner chính

Luồng v1:

```text
Raw video
  ↓ frame sampling
Motion signal + person candidate + brightness/blur/edge signal + scene-change signal
  ↓ candidate timestamp
Event merge
  ↓ candidate_events.csv
Proxy clip exporter
```

Các module tối thiểu:

1. motion candidate;
2. person candidate;
3. visual obstruction candidate;
4. global camera-change candidate;
5. event merger;
6. proxy clip exporter.

**Đầu ra B:** `candidate_mining_pipeline_v0.1`, `candidate_events_v0.1.csv`, `proxy_clips_batch_01`.

#### A

- Mapping candidate signal → test category.
- Chốt risk score và quota sample theo slice.
- Kiểm tra candidate có truy ngược tới `source_id`, timestamp, camera và ROI reference.

#### C

- Review tập nhỏ candidate: đúng/sai/bỏ sót/cắt thiếu context.
- Đề xuất pre-roll, post-roll, merge gap.

**Đầu ra chung:** `mining_validation_report`.

### Ngày 4 — Sampling có kiểm soát và phân loại thô

Ba luồng sampling bắt buộc:

| Luồng | Mục đích | Tỷ lệ khởi điểm |
|---|---|---:|
| Tool-selected candidates | Tăng tốc tìm positive candidate | 70% |
| Random background samples | Phản ánh production và phát hiện bias/bỏ sót mining | 20% |
| Risk-based samples | Bổ sung đêm, mưa, glare, rung, partial cover, edge case | 10% |

> Tỷ lệ là **sampling hypothesis v0.1**, có thể điều chỉnh sau mining validation; không phải quota bất biến.

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Phân nhóm happy path, edge, hard negative, adversarial, coverage slice; kiểm tra quota | `Sampling_Strategy_v1.0` |
| B | Chạy pipeline batch đầu, gộp/chuẩn hóa candidate, xuất manifest/proxy clip | `candidate_queue_v0.2`, `sampling_manifest_v0.1` |
| C | Review nhanh: đủ pre/post context, đánh dấu ambiguous/invalid, feedback cho mining | `Candidate_Review_Feedback` |

### Ngày 5 — Làm sạch bước đầu và review tuần

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Đánh giá coverage, xác định gap và quyết định yêu cầu thêm data/controlled scenario | `Coverage_Gap_Report_v0.1`, kế hoạch annotation Tuần 3 |
| B | Deduplicate, chuẩn hóa tên/format/timestamp, kiểm tra clip overlap, version manifest, đưa dữ liệu nhạy cảm vào storage kiểm soát | `dataset_manifest_draft_v0.1` |
| C | Review ngẫu nhiên từng category; đánh giá candidate precision sơ bộ; kiểm tra mining recall bằng random background; cập nhật guideline | `Annotation_Readiness_Report`, `Labeling_Guideline_v0.3` |

### Gate kết thúc Tuần 2

- [ ] Candidate truy ngược được về video nguồn, camera, timestamp và ROI reference.
- [ ] Có cả tool-selected, random background và risk-based sample.
- [ ] Không dùng output của mining như nhãn cuối.
- [ ] Có duplicate/leakage report và trạng thái eligibility rõ.
- [ ] Có annotation queue đủ context để review.
- [ ] Các coverage gap được ghi thành yêu cầu bổ sung hoặc limitation.

---

## Tuần 3 — Annotation, ground truth, KPI và bàn giao

> **Mục tiêu tuần:** tạo nhãn đáng tin cậy, khóa ground truth/version, tính KPI theo ba nhóm và hoàn thành bộ bàn giao.

### Ngày 1 — Calibration và khóa guideline

#### C — Chủ trì

1. Tổ chức calibration: A, B, C cùng gán 30–50 clip hoặc tập đại diện khả dụng.
2. So sánh event type, positive/negative, event start/end, severity, ambiguous/invalid.
3. Chốt các case khó: partial cover, glare/rain, temporary shake, sustained displacement, người ở ngoài ROI, nhiều event.

#### A

- Adjudicate case nghiệp vụ; liên hệ stakeholder nếu rule vẫn thiếu.
- Xác nhận guideline không mâu thuẫn với acceptance criteria/KPI.

#### B

- Chuẩn bị workspace/tool review; kiểm tra export annotation, source mapping và fields bắt buộc.

**Đầu ra:** `Labeling_Guideline_v1.0`, `Calibration_Result`, `Disagreement_Log`.

### Ngày 2 — Annotation vòng 1

Phân bổ khởi điểm:

| Người | Quota | Ưu tiên |
|---|---:|---|
| A | 25% | Use case nghiệp vụ, severity, edge case |
| B | 25% | Candidate kỹ thuật, cover/movement signal, log correlation |
| C | 50% | Điều phối, annotation chính, sample khó |

Trường metadata tối thiểu:

```text
sample_id
source_id
camera_id
roi_config_id
roi_version
event_label
ground_truth_status
event_start
event_end
expected_severity
lighting
distance
occlusion
motion_type
reviewer
review_timestamp
comment
```

**Quy tắc:** mọi clip thiếu context hoặc không thể kết luận phải là `ambiguous/invalid`, không ép thành positive/negative.

### Ngày 3 — Agreement, disagreement và schema validation

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| C | Chọn 10–20% clip cho hai người gán độc lập; đo percent agreement/Cohen’s Kappa (hoặc Fleiss’ Kappa), sai lệch start/end | `annotation_agreement_report`, `disagreement_queue` |
| A | Adjudicate disagreement nghiệp vụ; gửi stakeholder case không thể quyết định theo guideline | `Business_Adjudication_Log` |
| B | Validate schema: `start < end`, label hợp lệ, source/clip tồn tại, không duplicate sample ID, required fields đủ, ROI reference hợp lệ | `schema_validation_report` |

### Ngày 4 — Khóa ground truth, test set và KPI

#### C

- Xử lý disagreement; gắn cờ unresolved case.
- Khóa `ground_truth_v1.0`.
- Chọn golden set nhỏ nhưng tất cả sample phải có review/adjudication chất lượng cao.

#### B

Tạo cấu trúc logic:

```text
dataset/
├── benchmark/
│   ├── intrusion/
│   ├── camera_cover/
│   ├── camera_move/
│   └── negative/
├── production_distribution/
├── stress/                 # chỉ nếu có đủ dữ liệu/môi trường
├── golden/
├── manifests/
└── documentation/
```

- Khóa version/hashes/manifest.
- Tạo bảng TP/FP/FN/TN và tính KPI **tách riêng** cho intrusion, cover, movement.
- Không để clip cùng source-group xuất hiện ở nhiều tập độc lập.

#### A

- Review coverage theo use case, camera, ngày/đêm, event/negative, quality condition.
- Đối chiếu KPI với ngưỡng pass/fail.
- Không đánh dấu `Đạt` nếu sample chưa được khóa hoặc dữ liệu còn insufficient.

**Đầu ra:**

- `ground_truth_v1.0`
- `dataset_manifest_v1.0`
- `coverage_report_v1.0`
- `golden_set_v1.0`
- `kpi_result_v1.0`.

### Ngày 5 — Tài liệu hóa, review cuối và bàn giao

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Dataset card, test-data strategy, coverage report, limitation/assumption, acceptance checklist, handover minutes | `Dataset_Card_v1.0`, `Final_Handover_Minutes` |
| B | Pipeline README, requirements, cấu hình, hướng dẫn tái tạo candidate, version/hash/storage/permission | `Pipeline_README`, `Reproducibility_Guide` |
| C | Guideline final, annotation statistics, agreement report, ambiguous list, hướng dẫn review/update nhãn | `Annotation_Quality_Pack` |

### Gate kết thúc Tuần 3

- [ ] Guideline v1.0 đã khóa; review/ground truth có version.
- [ ] Disagreement được xử lý hoặc được ghi rõ là unresolved/ambiguous.
- [ ] Có schema validation, coverage report và manifest/hash.
- [ ] Có benchmark, production-distribution và golden set; golden không chứa ambiguous.
- [ ] KPI cho từng nhóm có TP/FP/FN/TN, công thức và evidence truy vết.
- [ ] Có dataset documentation và biên bản bàn giao.

---

## 8. Metric report template và pass/fail

### 8.1. Bảng confusion matrix theo từng nhóm

| Nhóm kịch bản | TP | FP | FN | TN | Precision | Recall | FP/(TP+FP) | Kết luận |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Trèo rào |  |  |  |  |  |  |  |  |
| Xoay camera |  |  |  |  |  |  |  |  |
| Che camera |  |  |  |  |  |  |  |  |

### 8.2. Quy tắc kết luận

| Trạng thái | Điều kiện |
|---|---|
| **Đạt** | Sample được khóa/review; Precision ≥ 90%, Recall ≥ 90%, FP/(TP+FP) ≤ 10% cho nhóm kịch bản tương ứng |
| **Không đạt** | Có đủ sample hợp lệ nhưng ít nhất một KPI không đạt |
| **Chưa kết luận** | Dữ liệu/số lượng sample không đủ, train leakage chưa xác minh, hoặc còn nhiều case unresolved/ambiguous |
| **Rủi ro chấp nhận** | Stakeholder phê duyệt chấp nhận limitation đã mô tả kèm tác động và kế hoạch xử lý |

### 8.3. Metric bổ sung khuyến nghị

Các metric này không thay thế KPI chính thức:

- false alerts/camera/day hoặc false alerts/camera/hour;
- số critical event bị bỏ sót;
- detection/alert latency p50, p95;
- sai số event start/end;
- tỷ lệ alert trùng;
- tỷ lệ candidate mining cần human correction.

---

## 9. Quy tắc dữ liệu, QC và bằng chứng

### 9.1. Kiểm soát leakage và duplicate

- Không để clip cùng `source_id`/camera/ngày/video nguồn xuất hiện ở các tập độc lập nếu có nguy cơ gần trùng.
- Test eligibility: `Test eligible`, `Train overlap`, `Suspected overlap`, `Unknown`.
- Nếu train list không có: báo cáo `Unknown`, không khẳng định test set độc lập.
- Deduplicate theo checksum/fingerprint và overlap thời gian; degraded video không tự động xóa nếu nó đại diện điều kiện thực tế.

### 9.2. Evidence tối thiểu cho mỗi sample/case

- sample/source/camera ID;
- video gốc hoặc proxy clip và timestamp;
- ROI config/version/snapshot reference;
- ground truth và reviewer;
- alert/log/response hệ thống;
- expected result, actual result, verdict;
- `run_id`, defect ID (nếu có), link evidence.

### 9.3. Kiểm soát thông tin nhạy cảm

- Video có mặt người/biển số phải lưu tại storage kiểm soát quyền truy cập.
- Masking/ẩn danh chỉ được áp dụng theo chính sách, nhưng không làm mất bằng chứng cần thiết để review.
- Manifest không lưu PII không cần thiết.

---

## 10. Deliverable theo tuần

| Tuần | Deliverable | Owner | Reviewer |
|---|---|---|---|
| 1 | Business clarification, objectives, use case, acceptance criteria, event/KPI rules | A | B, C, stakeholder |
| 1 | Technical readiness, ROI evidence checklist, pipeline/manifest design, dry-run evidence | B | A |
| 1 | Taxonomy, metadata schema, guideline v0.2, calibration plan | C | A, B |
| 2 | Video inventory, invalid/duplicate report, leakage/split/distribution report | B | A, C |
| 2 | Candidate pipeline, event manifest, proxy clips, sampling manifest | B | A, C |
| 2 | Coverage gap report, annotation readiness, guideline v0.3 | A/C | B |
| 3 | Guideline v1.0, annotation dataset, agreement/disagreement report | C | A, B |
| 3 | Schema validation, dataset manifest/hash, reproducibility guide | B | A, C |
| 3 | Ground truth, coverage report, golden set, KPI result | C/A | B |
| 3 | Dataset card, pipeline README, handover checklist/minutes | A | B, C |

---

## 11. Daily control, Definition of Done và rủi ro

### 11.1. Daily stand-up — 15 phút

Mỗi người trả lời:

1. Hôm qua đã hoàn thành gì và evidence ở đâu?
2. Hôm nay làm gì?
3. Blocker nào cần owner xử lý?
4. Có thay đổi nào ảnh hưởng dataset, guideline, KPI hoặc ROI evidence?

### 11.2. Daily status table

| Task | Owner | Status | Output/Evidence link | Issue | Next action |
|---|---|---|---|---|---|

Trạng thái dùng thống nhất:

```text
Not started
In progress
Blocked
Ready for review
Done
```

### 11.3. Rủi ro chính

| Rủi ro | Ảnh hưởng | Owner | Biện pháp |
|---|---|---|---|
| Không có train-data list | Không chứng nhận test độc lập | B | Gắn `Unknown`, ghi limitation |
| Cấp 2/3 hoặc event boundary mơ hồ | Nhãn/KPI không nhất quán | A/C | Khóa guideline; stakeholder adjudication |
| Video quá lớn/máy hạn chế | Chậm mining/review | B | Streaming, sampling, proxy clip, một worker/model nhỏ |
| Mining bỏ sót event | Dataset thiên lệch | B/C | Random background và risk-based sampling |
| Reviewer bị model output ảnh hưởng | Automation bias | C | Blind review, golden review độc lập |
| Nhiều clip trùng | KPI sai lệch | B | Source-group split, checksum/fingerprint |
| Không đủ positive event | Coverage thấp | A | Controlled scenario/synthetic data phase sau |
| Video có PII | Rủi ro bảo mật | B/C | Access control, retention/masking theo policy |
| KPI mẫu nhỏ | Kết luận không tin cậy | A | Ghi `Chưa kết luận`, nêu sample size/limitation |

---

## 12. Definition of Done

### Tuần 1 hoàn thành khi

- Có mục tiêu testing, use case, acceptance criteria và KPI calculation rule.
- Có event/ROI/severity rule đủ để gán nhãn.
- Câu hỏi chưa trả lời được ghi là assumption/blocker có owner.
- Có readiness/pipeline/metadata/taxonomy/guideline nháp.
- Có dry run evidence cho ba nhóm kịch bản.

### Tuần 2 hoàn thành khi

- Data đã inventory; duplicate/leakage/eligibility được báo cáo.
- Có candidate mining, proxy clips, sampling manifest gồm tool/random/risk stream.
- Candidate truy vết được về source và không được coi là ground truth.
- Có coverage gap và data sẵn sàng annotation.

### Tuần 3 hoàn thành khi

- Guideline khóa; annotation được review; disagreement xử lý.
- Ground truth/dataset manifest/golden set có version.
- KPI ba nhóm có evidence và kết luận đúng quy tắc.
- Có benchmark/production-distribution; stress set nếu đủ điều kiện.
- Có dataset documentation, reproducibility guide, checklist và handover minutes.

---

## 13. Phụ lục — Template test case

| Field | Nội dung |
|---|---|
| Test case ID | Ví dụ `INTR-ROI-RED-001` |
| Nhóm | Intrusion / Camera cover / Camera movement |
| Mục tiêu | Điều cần chứng minh |
| Tiền điều kiện | Camera, stream, ROI version, môi trường |
| Input/sample | `sample_id`, `source_id`, clip/path |
| Thao tác/kịch bản | Mô tả hành động thực tế |
| Ground truth | Nhãn, start/end, severity mong đợi |
| Kết quả mong đợi | Alert/type/severity/timestamp/evidence |
| Kết quả thực tế | Giá trị quan sát từ hệ thống |
| Phân loại KPI | TP / FP / FN / TN / Ambiguous / Invalid |
| Bằng chứng | Link video, snapshot ROI, log/alert |
| Người thực hiện/reviewer | Tên hoặc ID |
| Verdict/defect | Pass/Fail/Blocked và defect ID |

---

## 14. Kết quả kỳ vọng sau ba tuần

```text
Raw video
  ↓ Inventory & eligibility
Candidate mining
  ↓ Controlled sampling
Human review & calibration
  ↓ Ground truth / QC
Versioned test dataset
  ↓ KPI calculation
Golden regression set & handover
```

Giá trị dài hạn của kế hoạch không chỉ là số clip đã gán nhãn, mà là quy trình tái sử dụng được khi có camera mới, điều kiện môi trường mới hoặc model phiên bản mới: chạy lại inventory/mining, review theo guideline, phát hành dataset version mới và chạy golden regression.
