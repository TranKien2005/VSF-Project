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

Việc **vẽ, tạo hoặc thay đổi ROI không nằm trong phạm vi** kế hoạch này. Trong Tuần 1, nhóm chỉ thiết kế schema/checklist để nhận và lưu evidence ROI; chưa xác nhận snapshot/version thực tế vì chưa có data/source thật. Từ Tuần 2, khi có video/source, mỗi case phụ thuộc ROI cần lưu bằng chứng cấu hình đang áp dụng:

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

| Nhãn sự kiện | Diễn giải | ROI/category evidence | Severity |
|---|---|---|---|
| `person_near_fence` | Đối tượng lảng vảng ở vùng ngoài hàng rào | ROI Xanh khi evidence ROI xác nhận. | Chỉ ghi output rule engine nếu hệ thống cung cấp; không tự gán Cấp 4. |
| `person_approaching_fence` | Đối tượng tiếp cận sát hàng rào | ROI Vàng khi evidence ROI xác nhận. | Không dùng reviewer để phân biệt Cấp 2/Cấp 3. |
| `person_touching_fence` | Đối tượng chạm/bám hàng rào | ROI Vàng/Đỏ theo ROI thực tế. | Chỉ ghi output rule engine nếu có. |
| `person_climbing_fence` | Đối tượng có hành vi trèo rào | ROI liên quan theo evidence video/reference. | Chỉ ghi output rule engine nếu có. |
| `person_on_fence_top` | Đối tượng ở đỉnh hàng rào | ROI liên quan theo evidence video/reference. | Chỉ ghi output rule engine nếu có. |
| `person_crossing_fence` | Đối tượng vượt qua hàng rào | ROI Đỏ khi evidence ROI xác nhận. | Rule engine quyết định Cấp 1 nếu rule hệ thống áp dụng. |
| `person_inside_restricted_area` | Đối tượng ở trong khu vực cấm | ROI Đỏ khi evidence ROI xác nhận. | Rule engine quyết định severity. |
| `person_outside_roi` | Có người nhưng ngoài vùng cảnh báo | Negative/hard negative. | Không áp dụng. |

> Lảng vảng tối đa 5 phút/ROI Xanh và các cấp cảnh báo là reference cho rule engine. Candidate mining và reviewer không tạo label `loitering`, không dùng ngưỡng 5 phút để chia candidate, và không tự gán severity.

### 4.2. Che camera/tamper và nhiễu liên quan

| Nhãn | Vai trò / rule |
|---|---|
| `lens_full_cover` | Positive khi evidence che đáp ứng ≥30% khung hình và kéo dài ≥120 giây. |
| `lens_partial_cover` | Positive nếu tổng evidence vẫn đáp ứng ≥30% và ≥120 giây; nếu dưới một trong hai ngưỡng thì boundary/negative. |
| `cover_below_area_threshold` | Boundary/negative: che dưới 30%. |
| `cover_below_duration_threshold` | Boundary/negative: che ≥30% nhưng dưới 120 giây. |
| `temporary_occlusion` | Edge/negative: vật che tạm thời, không đáp ứng đủ 30%/120 giây. |
| `rain_heavy`, `water_drop_or_fog` | Environmental hard negative hoặc camera-health riêng nếu system rule chưa xác định. |
| `headlight_glare` | Hard negative: ánh đèn xe quét qua. |
| `low_light` | Quality condition/hard negative. |
| `black_screen`, `video_freeze`, `video_loss` | Camera health riêng hay tamper: ghi riêng, không tự gộp vào cover nếu chưa có rule hệ thống. |

> Severity cover do rule engine quyết định. Mentor cung cấp reference Cấp 1; reviewer chỉ ghi severity output thực tế của hệ thống nếu có.

### 4.3. Rung lắc/xoay camera

| Nhãn | Diễn giải |
|---|---|
| `camera_strong_shake` | Positive: camera rung mạnh theo evidence video. Không tự đặt ngưỡng pixel/độ/thời lượng. |
| `camera_rotation` | Positive: camera bị xoay/lệch hướng theo evidence video. |
| `temporary_shake` | Edge/negative: rung ngắn rồi trở lại bình thường khi evidence chưa đủ để coi là rung mạnh. |
| `environmental_vibration` | Hard negative/edge: rung do gió, xe, cổng hoặc điều kiện ngoài ý muốn. |
| `sustained_camera_displacement` | Mô tả kỹ thuật có thể dùng cho evidence xoay/lệch hướng; không tự tạo threshold mới. |
| `roi_drift` | Ghi nhận evidence nếu ROI không còn bám vùng vật lý; không tự biến thành category alert riêng nếu system rule chưa xác định. |
| `scene_change_non_camera_move` | Cảnh thay đổi nhưng camera không bị dịch chuyển; hard negative. |

> Severity movement do rule engine quyết định. Mentor cung cấp reference Cấp 1 cho rung mạnh/xoay; reviewer chỉ ghi output system nếu có.

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

## 6. Fact đã có và điểm cần chuẩn bị trong Tuần 1

Tuần 1 chỉ thiết kế rule/spec/template, chưa có raw data để xác minh case thật. Các fact mentor đã trả lời không tiếp tục được ghi như câu hỏi/blocker; điểm chưa có thông tin được ghi rõ để áp dụng từ Tuần 2, không gán owner/approval/deadline giả.

| Nội dung | Fact / trạng thái hiện có | Việc chuẩn bị trong Tuần 1 | Ảnh hưởng khi execution |
|---|---|---|---|
| Object scope | Bài toán VHR hiện tập trung vào person. Whitelist/nhân viên/xe/động vật chưa có rule cụ thể. | Ghi person là scope hiện có; thiết kế trạng thái negative/unknown cho case ngoài scope. | Không suy diễn policy authorization; chỉ report limitation nếu gặp case thực tế. |
| ROI evidence | Có ROI Xanh/Vàng/Đỏ; cách lấy `roi_config_id`, version/snapshot/effective time cần xác nhận khi có system/data access. | Thiết kế schema/checklist ROI evidence. | Case ROI thiếu reference phải ghi limitation, không tạo/sửa ROI. |
| Cấp 2/Cấp 3 | Severity do rule engine quyết định; phân loại video không cần tách Cấp 2/Cấp 3. | Tách `review_category`/`roi_zone` khỏi `rule_engine_severity_output` trong schema. | Chỉ verify severity khi có system output/rule reference. |
| Event boundary | Chưa có video thật để kiểm chứng boundary case. | Thiết kế guideline start/end, ambiguous/invalid và test-case template. | Hiệu chỉnh guideline từ review data Tuần 2; unresolved case không vào KPI. |
| Chuyển ROI/dedup | Chưa có incident/cooldown rule cụ thể. | Thiết kế field event/alert matching, duplicate và misclassification trong KPI template. | Nếu thiếu rule/matching window thì KPI phần liên quan là Chưa kết luận. |
| Cover/tamper | **Đã trả lời:** cover positive khi ≥30% và ≥120 giây. Rain/glare là interference; freeze/black screen/video loss chưa có rule rõ. | Đưa 30%/120s vào taxonomy, acceptance, boundary cases và annotation schema. | Không tự gộp camera-health vào cover. |
| Camera movement | **Đã trả lời:** strong shake hoặc rotation/lệch hướng. Chưa có pixel/degree/duration threshold. | Thiết kế positive/negative/uncertain labels và evidence fields. | Chỉ dùng obvious strong-shake/rotation cho positive; case nhẹ/không rõ là edge/uncertain. |
| KPI | Kế hoạch dùng event-level; M2 = `FP/(TP+FP)`. | Hoàn thiện metric/matching template, exclusion và report conditions. | Không có evidence/matching rule đủ thì không công bố KPI chính thức. |
| Latency/SLA | Chưa có detection window/latency origin từ hệ thống. | Để field observed timestamp trong schema, không đặt target giả. | Không tính latency chính thức nếu không có rule/time origin. |
| Data/train leakage | Chưa có train manifest/source list. | Thiết kế eligibility field: Test eligible/Train overlap/Suspected overlap/Unknown. | Mặc định `Unknown`, không claim test độc lập. |
| Ground truth/review | Chưa có data thật để annotation/calibration. | Thiết kế labeling guideline, second-review, disagreement và release criteria. | Chỉ lock ground truth sau review evidence thực tế. |
| PII/storage | Raw video/artifact nhạy cảm phải local-only/Git-ignore; retention/access chi tiết chưa có. | Thiết kế local storage/Git policy. | Không commit raw, JSON, export, model/cache/log; ghi limitation nếu policy chi tiết chưa có. |

---

## 7. Kế hoạch chi tiết theo tuần và từng người

## Tuần 1 — Nắm bài toán, thiết kế plan và base pipeline

> **Ràng buộc đầu vào:** Tuần 1 (ngày 16–17) **chưa có raw video/data thật**. Vì vậy toàn bộ output của tuần này là plan, specification, schema, template và base pipeline; không có inventory, candidate, review clip, annotation, ground truth, coverage result, leakage result hay KPI result thực tế.
>
> **Mục tiêu tuần:** chuyển requirement mentor thành scope/use case/metric/acceptance rõ ràng; thiết kế pipeline và contract để nhận data từ Tuần 2; lập schedule chi tiết theo vai trò cho phần việc còn lại.

### Phân biệt output Tuần 1 và artifact có data

| Loại output | Tuần 1 | Từ Tuần 2 khi có raw data |
|---|---|---|
| Tài liệu | Plan, rule spec, use-case catalogue, schema, template, guideline draft, pipeline design | Report dựa trên dữ liệu thực tế, release note, coverage/KPI/ground-truth document |
| Data artifact | Chỉ folder structure/template rỗng nếu cần | Inventory, checksum, candidate JSON/manifest, queue, annotation, ground truth, validation và KPI input/result |
| Candidate mining | Chuẩn bị môi trường/base pipeline, định nghĩa input/output, kiểm thử unit/synthetic fixture nếu có | Chạy trên raw source thực tế để tạo technical evidence |
| Review/annotation | Thiết kế guideline, queue schema và QC protocol | Review video thật, annotation, agreement, disagreement và ground truth |

### Ngày 16 — Xác định scope, use case và thiết kế contract

> Không tổ chức hoặc ghi nhận kickoff/meeting giả. Hoạt động ngày 16 là đọc requirement mentor, thiết kế tài liệu và chuẩn bị base pipeline không cần raw data.

#### A — QA Lead / Test Design

1. Chuyển thông tin mentor thành mục tiêu test, phạm vi và ngoài phạm vi.
2. Soạn use case cho intrusion theo ROI Xanh/Vàng/Đỏ, cover ≥30%/≥120 giây, strong shake/rotation và negative/interference.
3. Thiết kế KPI event-level: TP/FP/FN/TN, Precision, Recall, `FP/(TP+FP)`, duplicate, misclassification và điều kiện `Chưa kết luận`.
4. Thiết kế pass/fail/acceptance theo category/evidence; severity là output rule engine, không phải nhãn do reviewer chọn.

**Đầu ra tài liệu:**

- `AI_Testing_Objectives_v0.1`
- `Use_Case_Catalogue_v0.1`
- `Metric_and_KPI_Calculation_Rule_v0.1`
- `Acceptance_Criteria_Draft_v0.1`

#### B — Data & Automation

1. Thiết kế cấu trúc data folder local, manifest, source identity, checksum, source-relative timestamp và data lifecycle.
2. Thiết kế base candidate-mining pipeline; ghi rõ output hiện tại chỉ là person technical evidence, không phải intrusion/ROI/cover/movement/severity label.
3. Soạn checklist sẽ dùng từ Tuần 2 để inventory source, nhận ROI evidence và kiểm tra quyền truy cập video/log/API nếu được cung cấp.
4. Chuẩn bị environment/tooling và test code bằng unit test hoặc fixture không nhạy cảm; không chạy trên raw camera video vì chưa có data.

**Đầu ra tài liệu:**

- `Dataset_Folder_and_Manifest_Design_v0.1`
- `Candidate_Mining_Pseudocode_v0.1`
- `Technical_Readiness_Checklist_v0.1`
- `Camera_Stream_and_ROI_Evidence_Checklist_v0.1`
- `KPI_Calculation_Sheet_Template_v0.1`

#### C — Annotation & Data Quality

1. Soạn taxonomy nhãn và metadata schema từ requirement mentor.
2. Soạn guideline draft: category, source-relative event boundary, ROI evidence, cover percentage/duration, movement evidence, ambiguous/invalid.
3. Thiết kế queue entry template, blind/second review, agreement, disagreement và adjudication process.
4. Không tạo annotation/calibration result vì chưa có sample thật.

**Đầu ra tài liệu:**

- `Label_Taxonomy_v0.1`
- `Metadata_Schema_v0.1`
- `Labeling_Guideline_v0.1`
- `Annotation_Queue_Entry_Template_v0.1`
- `Disagreement_and_Adjudication_Process_v0.1`

### Ngày 17 — Hoàn thiện plan tuần 2–3 và chuẩn bị nhận data

#### Công việc chung

1. Review chéo các plan/spec/template tạo ngày 16 để loại mâu thuẫn.
2. Ghi các requirement đã có mentor answer là fact; không tiếp tục đưa thành câu hỏi/blocker.
3. Các điểm chưa có dữ liệu đầu vào hoặc rule-system output chỉ được ghi limitation/dependency của execution, không tự suy diễn.
4. Lập detailed schedule cho Tuần 2 (raw → coarse auto → fine human → cleaning) và Tuần 3 (annotation → ground truth → QC → storage → handover).

#### A — QA Lead / Test Design

1. Hoàn thiện acceptance draft, coverage hypothesis, requirement traceability và risk/limitation plan.
2. Chuyển cover threshold 30%/120s vào acceptance/use case; tách ROI category khỏi severity verification.
3. Xác định coverage slices sẽ đánh giá khi data đến: camera, ngày/đêm, ROI, scenario, condition, positive/negative/edge.

**Đầu ra tài liệu:**

- `Acceptance_Criteria_v1.0`
- `Requirement_Traceability_Matrix_v1.0`
- `Coverage_Quota_v1.0`
- `Risk_and_Dependency_Log_v1.0`
- `Three_Week_Execution_Matrix_v1.0`

#### B — Data & Automation

1. Hoàn thiện pipeline/manifest design và validation rules cho inventory, source group, duplicate/leakage, candidate queue và KPI input.
2. Xác định rõ artifact nào là planned document, artifact nào chỉ được sinh local từ raw data ở Tuần 2 trở đi.
3. Chuẩn bị command/runbook nhận dữ liệu, nhưng không ghi dry-run evidence report hoặc inventory result khi chưa có data.

**Đầu ra tài liệu:**

- `Data_Pipeline_Architecture_v1.0`
- `Data_Receipt_and_Inventory_Runbook_v1.0`
- `Leakage_and_Source_Group_Policy_v1.0`
- `Candidate_and_Evidence_Data_Contract_v1.0`
- `Local_Artifact_and_Git_Policy_v1.0`

#### C — Annotation & Data Quality

1. Hoàn thiện guideline draft, annotation schema, calibration plan và agreement protocol.
2. Xác định sample selection/second-review criteria để áp dụng khi queue có dữ liệu thật.
3. Không viết calibration result, disagreement log hoặc ground truth release vì các artifact đó cần video và annotation thật.

**Đầu ra tài liệu:**

- `Labeling_Guideline_v0.2`
- `Annotation_QC_Protocol_v1.0`
- `Calibration_Plan_v1.0`
- `Annotation_Agreement_Plan_v1.0`
- `Ground_Truth_Release_Criteria_v1.0`

### Gate kết thúc Tuần 1

Chỉ chuyển sang execution trên raw data ở Tuần 2 khi:

- [ ] Có plan/scope/use case/acceptance/KPI rule/spec và template cần thiết.
- [ ] Cover ≥30%/≥120s đã được đưa vào taxonomy/acceptance.
- [ ] Đã tách ROI category, review label và rule-engine severity output.
- [ ] Có folder/manifest/schema/runbook thiết kế để nhận data.
- [ ] Base pipeline/environment sẵn sàng theo checklist.
- [ ] Không có artifact nào giả định đã quét/review/chạy trên raw video thật.

---

## Tuần 2 — Raw video đến candidate annotation queue

> **Mục tiêu tuần:** từ raw data thực nhận, thực hiện inventory/eligibility, phân loại thô bằng automation, phân loại tinh bởi người review, sau đó làm sạch và chuẩn bị annotation queue. **Chưa tuyên bố đây là ground truth cuối.**
>
> Output có raw video/annotation/manifest/report là local artifact Git-ignore. Các tên document trong kế hoạch mô tả report/spec cần tạo sau execution; không được xem là đã tồn tại trước khi nhận data.

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

### Ngày 3 — Phân loại thô bằng automation và tạo candidate evidence

#### B — Data & Automation

Chạy pipeline trên raw data theo capability thực tế, lưu source-relative timestamp và technical evidence để hỗ trợ review.

**Capability hiện tại của POC:** RT-DETR person detection tạo một JSON local theo raw source trong `person_detected`; viewer đọc raw source và JSON. POC không tự kết luận intrusion/ROI/cover/movement/severity và không tự tạo inventory, CSV manifest, proxy clip hoặc review video hàng loạt.

Target workflow khi các module tương ứng đã được triển khai/được phép chạy:

```text
Raw video
  ↓ inventory + frame sampling
Technical candidate signals
  ↓ source-relative candidate windows
Event merge / context policy
  ↓ local candidate evidence and queue records
Human review
```

Các luồng coarse classification cần được thiết kế và ghi rõ status capability:

1. happy path/normal candidates;
2. edge candidates: ROI boundary, cover area/duration boundary, uncertain movement;
3. negative/interference: rain, glare, person outside relevant ROI, non-camera scene motion;
4. random background samples để kiểm tra mining bias/bỏ sót;
5. risk-based samples: đêm, mưa, glare, rung, partial cover và edge case.

**Đầu ra tài liệu:**

- `Candidate_Mining_Runbook_v1.0` — input/output, source-time semantics, capability hiện tại và target modules.
- `Coarse_Classification_Plan_v1.0` — happy/edge/negative/random/risk streams.
- `Candidate_Mining_Validation_Report_v0.1` — chỉ tạo sau khi review output raw-data thực tế.

**Đầu ra local sau khi chạy:** person detection JSON hiện có; candidate queue/manifest/cover/movement evidence chỉ tạo khi corresponding pipeline capability tồn tại.

#### A — QA / Test Design

- Mapping candidate reason → test category chỉ là hỗ trợ sampling, không phải final label.
- Kiểm tra coarse streams bao phủ normal, edge, negative/interference theo taxonomy Mục 4.
- Ghi coverage gap hoặc capability gap thay vì tự coi module chưa có là đã chạy.

#### C — Annotation & Data Quality

- Review một tập candidate có context để đánh giá đủ/thiếu context, false candidate và missed-candidate risk.
- Ghi feedback cho mining; không dùng output mining làm final ground truth.
- Chỉ đề xuất pre-roll/post-roll/merge-gap như technical review feedback, không biến thành event/severity rule nghiệp vụ.

**Đầu ra chung:** `Mining_Validation_Report_v0.1` sau khi có raw-data execution và human review.

### Ngày 4 — Sampling có kiểm soát, phân loại tinh bởi con người

Ba luồng sampling bắt buộc:

| Luồng | Mục đích | Tỷ lệ khởi điểm |
|---|---|---:|
| Tool-selected candidates | Tăng tốc tìm positive candidate; không thay nhãn người review | 70% |
| Random background samples | Phản ánh production, kiểm tra bias/bỏ sót mining | 20% |
| Risk-based samples | Bổ sung đêm, mưa, glare, rung, cover boundary và edge case | 10% |

> Tỷ lệ là **sampling hypothesis v0.1**, được điều chỉnh theo inventory/mining validation; không phải quota bất biến.

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Phân nhóm happy path, edge, hard negative, adversarial/interference và coverage slice; kiểm tra quota. | `Sampling_Strategy_v1.0` |
| B | Gộp/chuẩn hóa candidate evidence theo source/time; chỉ export clip khi operator/reviewer chủ động cần context. | local candidate queue/manifest theo capability thực tế |
| C | Review nhanh category, context, ROI evidence, cover area/duration hoặc movement evidence; đánh dấu `ambiguous/invalid` khi không đủ bằng chứng. | `Candidate_Review_Feedback`, `Annotation_Queue_Entry_Template` |

### Ngày 5 — Làm sạch bước đầu và review tuần

| Vai trò | Công việc | Đầu ra |
|---|---|---|
| A | Đánh giá coverage, gap và nhu cầu data bổ sung/controlled scenario. | `Coverage_Gap_Report_v0.1`, kế hoạch annotation Tuần 3 |
| B | Deduplicate, chuẩn hóa tên/format/timestamp, kiểm tra overlap/source-group, version local manifest và local storage policy. | `dataset_manifest_draft_v0.1`, `Data_Cleaning_and_Validation_Report_v0.1` |
| C | Review ngẫu nhiên các category; đánh giá annotation readiness và cập nhật guideline theo ambiguity thực tế. | `Annotation_Readiness_Report`, `Labeling_Guideline_v0.3` |

**Quy tắc xử lý/cleaning:**

- Chuẩn hóa `sample_id`, `source_id`, `camera_id`, source-relative timestamp, category và evidence reference.
- Validate `start < end`, source tồn tại, required fields, label vocabulary và duplicate IDs.
- Không xóa difficult-but-valid data chỉ để làm đẹp metric.
- PII/raw video/JSON/export giữ local-only; chỉ áp dụng masking/ẩn danh khi có policy và không làm mất evidence review.
- Đo class imbalance và dùng sampling/coverage để xử lý; không synthetic balance/duplicate sample khi chưa có phương án được phép.

**Đầu ra tài liệu:** `Sensitive_Data_Handling_Policy_v1.0`, `Class_Balance_and_Sampling_Decision_v1.0`, `Week_2_Exit_Checklist_v1.0`.

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
2. So sánh event type, positive/negative, event start/end, ROI evidence, cover-rule satisfaction, ambiguous/invalid; severity chỉ đối chiếu với rule-engine output khi có.
3. Chốt cách xử lý các case khó: partial cover, glare/rain, temporary shake, sustained displacement, người ở ngoài ROI, nhiều event.

#### A

- Adjudicate case theo guideline/evidence; case thiếu rule-system output hoặc evidence được ghi unresolved/limitation, không tự suy diễn.
- Xác nhận guideline không mâu thuẫn với acceptance criteria/KPI.

#### B

- Chuẩn bị workspace/tool review; kiểm tra export annotation, source mapping và fields bắt buộc.

**Đầu ra:** `Labeling_Guideline_v1.0`, `Calibration_Result`, `Disagreement_Log`.

### Ngày 2 — Annotation vòng 1

Phân bổ khởi điểm:

| Người | Quota | Ưu tiên |
|---|---:|---|
| A | 25% | Use case nghiệp vụ, ROI/category evidence, edge case |
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
roi_zone
rule_engine_rule_id
rule_engine_rule_version
rule_engine_severity_output
cover_area_percent
cover_duration_seconds
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
| A | Adjudicate disagreement theo guideline/evidence; ghi unresolved/limitation nếu case không thể quyết định. | `Business_Adjudication_Log` |
| B | Validate schema: `start < end`, label hợp lệ, source/clip tồn tại, không duplicate sample ID, required fields đủ, ROI reference hợp lệ | `schema_validation_report` |

### Ngày 4 — Khóa ground truth, test set và KPI

#### C — Annotation & Data Quality

- Xử lý disagreement; gắn cờ unresolved/ambiguous/invalid case.
- Khóa `ground_truth_v1.0` chỉ với sample có review/adjudication/evidence đủ điều kiện.
- Chọn golden set nhỏ; không đưa ambiguous, invalid, unresolved hoặc sample thiếu traceability vào golden set.

#### B — Data & Automation

Thiết kế và áp dụng cấu trúc logic local cho dataset/reference:

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

- Khóa version/hashes/manifest của record/reference; raw video và generated sensitive artifacts vẫn local/Git-ignore.
- Tạo bảng TP/FP/FN/TN và KPI **tách riêng** cho intrusion, cover, movement khi đủ event matching, alert evidence và ground truth.
- Tách `review_category`/`roi_zone` khỏi `rule_engine_severity_output`.
- Không để clip cùng source-group xuất hiện ở nhiều tập độc lập.

#### A — QA / Test Design

- Review coverage theo use case, camera, ngày/đêm, event/negative, quality condition.
- Đối chiếu KPI với ngưỡng pass/fail chỉ trên sample eligible.
- Không đánh dấu `Đạt` nếu sample chưa khóa, rule matching thiếu, alert/rule-engine output không đủ hoặc dữ liệu insufficient.

**Đầu ra local sau execution:**

- `ground_truth_v1.0`
- `dataset_manifest_v1.0`
- `coverage_report_v1.0`
- `golden_set_v1.0`
- `kpi_result_v1.0` hoặc report `Chưa kết luận` có limitation rõ ràng.

**Đầu ra tài liệu:** `Ground_Truth_Release_Note_v1.0`, `Dataset_Version_and_Change_Log_v1.0`, `KPI_Evaluation_Report_v1.0`, `Golden_Set_Release_Note_v1.0`.

### Ngày 5 — Tài liệu hóa, review cuối và bàn giao

| Vai trò | Công việc | Đầu ra tài liệu |
|---|---|---|
| A | Dataset card, test-data strategy, coverage report, limitation/assumption và acceptance/handover checklist. | `Dataset_Card_v1.0`, `Final_Handover_Checklist_v1.0`, `Handover_Summary_v1.0` |
| B | Pipeline README, requirements/configuration, hướng dẫn tái tạo candidate evidence, version/hash/storage/permission. | `Pipeline_README`, `Reproducibility_Guide`, `Controlled_Storage_and_Access_Guide_v1.0` |
| C | Guideline final, annotation statistics, agreement report, ambiguous list và hướng dẫn review/update label. | `Annotation_Quality_Pack`, `Annotation_Agreement_Report_v1.0` |

### Gate kết thúc Tuần 3

- [ ] Guideline v1.0 đã khóa; review/ground truth có version.
- [ ] Disagreement được xử lý hoặc được ghi rõ là unresolved/ambiguous/invalid.
- [ ] Có schema validation, coverage report và manifest/hash/reference.
- [ ] Có benchmark, production-distribution và golden set; golden không chứa ambiguous/invalid/unresolved.
- [ ] KPI cho từng nhóm có TP/FP/FN/TN, công thức và evidence truy vết hoặc ghi `Chưa kết luận` có lý do.
- [ ] Rule-engine severity chỉ được report khi có output/rule reference; không phải reviewer label.
- [ ] Có dataset documentation, reproducibility guide và handover checklist/summary.

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
| **Rủi ro chấp nhận** | Limitation được ghi rõ tác động, evidence hiện có và kế hoạch xử lý tiếp theo; không biến limitation thành kết luận KPI đạt. |

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
- video gốc và source-relative timestamp; local export clip chỉ là evidence phụ khi reviewer chủ động tạo;
- ROI config/version/snapshot reference khi use case phụ thuộc ROI;
- ground truth/category và reviewer;
- alert/log/response hệ thống khi có quyền truy cập;
- expected category/rule evidence, actual system output, verdict;
- `rule_engine_rule_id`/version và `rule_engine_severity_output` khi hệ thống cung cấp;
- `cover_area_percent`/`cover_duration_seconds` khi use case là cover;
- `run_id`, defect ID (nếu có), link evidence.

### 9.3. Kiểm soát thông tin nhạy cảm

- Video có mặt người/biển số phải lưu tại storage kiểm soát quyền truy cập.
- Masking/ẩn danh chỉ được áp dụng theo chính sách, nhưng không làm mất bằng chứng cần thiết để review.
- Manifest không lưu PII không cần thiết.

---

## 10. Deliverable theo tuần

| Tuần | Deliverable | Owner | Reviewer |
|---|---|---|---|
| 1 | Scope/use case/acceptance/KPI documents: mô tả model evaluation, category, ROI/severity boundary, pass/fail và metric rule; chưa có kết quả data thực tế | A | B, C |
| 1 | Technical design documents: readiness checklist, ROI-evidence checklist, folder/manifest/pipeline design, inventory/leakage/KPI-input template; không có dry-run evidence | B | A |
| 1 | Annotation design documents: taxonomy, metadata schema, guideline v0.2, calibration/agreement/queue plan; chưa có annotation hoặc calibration result | C | A, B |
| 2 | Video inventory, invalid/duplicate report, leakage/split/distribution report | B | A, C |
| 2 | Candidate evidence theo capability thực tế, sampling manifest tool/random/risk, mining validation và annotation readiness; export clip chỉ thủ công khi cần context | B | A, C |
| 2 | Coverage gap report, annotation readiness, guideline v0.3 | A/C | B |
| 3 | Guideline v1.0, annotation dataset, agreement/disagreement report | C | A, B |
| 3 | Schema validation, dataset manifest/hash, reproducibility guide | B | A, C |
| 3 | Ground truth, coverage report, golden set, KPI result | C/A | B |
| 3 | Dataset card, pipeline README, reproducibility guide, handover checklist/summary | A | B, C |

---

## 11. Daily control, Definition of Done và rủi ro

### 11.1. Daily coordination — 15 phút

Đây là nhịp phối hợp nội bộ khi nhóm thực hiện, không phải biên bản một cuộc họp đã diễn ra. Mỗi người cập nhật:

1. Hôm trước đã hoàn thành gì và evidence/document ở đâu?
2. Hôm nay làm gì?
3. Limitation hoặc dependency nào ảnh hưởng execution?
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

| Rủi ro | Ảnh hưởng | Phụ trách nội bộ | Biện pháp |
|---|---|---|---|
| Không có train-data list | Không chứng nhận test độc lập | B | Gắn `Unknown`, ghi limitation |
| Cấp 2/3, event boundary hoặc rule-engine output thiếu | Severity/KPI verification không nhất quán | A/C | Video review chỉ ghi category/ROI; ghi unresolved/limitation, không tự suy diễn severity. |
| Video quá lớn/máy hạn chế | Chậm mining/review | B | Streaming, sampling, seek theo timestamp và manual export clip khi cần context |
| Mining bỏ sót event | Dataset thiên lệch | B/C | Random background và risk-based sampling |
| Reviewer bị model output ảnh hưởng | Automation bias | C | Blind review, golden review độc lập |
| Nhiều clip trùng | KPI sai lệch | B | Source-group split, checksum/fingerprint |
| Không đủ positive event | Coverage thấp | A | Ghi coverage gap; controlled scenario/synthetic data chỉ là phase sau nếu được phép |
| Video có PII | Rủi ro bảo mật | B/C | Local access control, retention/masking theo policy |
| KPI mẫu nhỏ | Kết luận không tin cậy | A | Ghi `Chưa kết luận`, nêu sample size/limitation |

---

## 12. Definition of Done

### Tuần 1 hoàn thành khi

- Có mục tiêu testing, use case, acceptance criteria và KPI calculation rule.
- Cover ≥30%/≥120s, ROI category và rule-engine severity boundary được đưa đúng vào taxonomy/guideline.
- Các điểm chưa có system/data evidence được ghi limitation/dependency, không gán owner/approval giả và không tự suy diễn rule.
- Có readiness/pipeline/metadata/taxonomy/guideline nháp cùng folder/manifest/template để nhận data.
- **Không yêu cầu dry run evidence, inventory, candidate, review clip, annotation hay KPI result**, vì raw data chỉ được nhận từ Tuần 2.

### Tuần 2 hoàn thành khi

- Data đã inventory; duplicate/leakage/eligibility được báo cáo.
- Có candidate evidence và sampling manifest gồm tool/random/risk stream theo capability thực tế; manual export clip chỉ tạo khi reviewer/operator chủ động cần context.
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
| Ground truth | Nhãn/category, start/end, ROI evidence; severity không do reviewer tự gán |
| Kết quả mong đợi | Alert/type/timestamp/evidence; `rule_engine_severity_output` chỉ khi system rule/output có sẵn |
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
