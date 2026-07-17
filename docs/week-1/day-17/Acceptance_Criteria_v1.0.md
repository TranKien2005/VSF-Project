# Acceptance Criteria v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Reviewer:** B (data/KPI input), C (taxonomy, boundary, ambiguous), Stakeholder (phê duyệt)
> **Nguồn requirement:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 2, 3, 8
> **Đầu vào ngày 16:** [`Business_Clarification_Log_v0.1`](../day-16/Business_Clarification_Log_v0.1.md), [`Assumption_and_Blocker_Log_v0.1`](../day-16/Assumption_and_Blocker_Log_v0.1.md), [`Use_Case_Catalogue_v0.1`](../day-16/Use_Case_Catalogue_v0.1.md)

## 0. Trạng thái phát hành

> **Đánh số `v1.0` theo tên artifact quy định trong kế hoạch, nhưng tài liệu CHƯA được khóa.**
> Tại thời điểm phát hành, không có câu hỏi nghiệp vụ nào từ ngày 16 ở trạng thái `Answered`. Các tiêu chí phụ thuộc severity, event boundary, cover threshold và movement threshold vẫn ở `TBD_STAKEHOLDER_APPROVAL`.

```text
Status: ASSUMPTION
Approval required from: Mentor/Stakeholder
Impact: KPI chưa được coi là kết quả chính thức
Fallback: Áp dụng rule tạm thời để dry-run, không khóa golden set
```

## 1. Phạm vi

- Trèo rào/xâm nhập.
- Che camera/tamper.
- Rung lắc hoặc xoay lệch camera.
- Data quality và traceability.
- E2E alert evidence: đúng camera, timestamp, loại sự kiện/cấp độ và có bằng chứng clip/log.

Ngoài phạm vi v1: thay đổi/huấn luyện model, thay đổi ROI production, pentest, multi-camera tracking, stress test quy mô lớn, nhận dạng danh tính, synthetic data quy mô lớn.

## 2. KPI bắt buộc

| Nhóm | Recall (M1) | Precision (M3) | Tỷ lệ báo động giả (M2) |
|---|---:|---:|---:|
| Trèo rào/xâm nhập | ≥ 90% | ≥ 90% | ≤ 10% |
| Che camera | ≥ 90% | ≥ 90% | ≤ 10% |
| Camera movement | ≥ 90% | ≥ 90% | ≤ 10% |

KPI tính riêng cho từng nhóm và tính theo **event**, không theo frame. Quy tắc đếm chi tiết: [`Metric_and_KPI_Calculation_Rule_v1.0.md`](./Metric_and_KPI_Calculation_Rule_v1.0.md).

## 3. Acceptance criteria

### 3.1. Intrusion

| ID | Use case | Điều kiện đạt | Evidence bắt buộc | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| AC-INT-001 | UC-INT-004, UC-INT-005 — trèo rào | Alert intrusion đúng loại trong detection window | Video, event ID, alert ID, timestamp, ROI version | BL-003, BL-009 | Draft |
| AC-INT-002 | UC-INT-006 — vượt rào | Alert Cấp 1 trong detection window của Cấp 1 | Video, ROI Đỏ reference, alert log, timestamp | BL-003, BL-009 | Draft |
| AC-INT-003 | UC-INT-007 — trong khu vực cấm | Alert Cấp 1 | Video, ROI reference, alert log | BL-009 | Draft |
| AC-INT-004 | UC-INT-002, UC-INT-003 — tiếp cận/chạm rào | Alert đúng severity theo rule Cấp 2/Cấp 3 đã chốt | Video, ROI reference, alert log | BL-001 — `TBD_STAKEHOLDER_APPROVAL` | Blocked |
| AC-INT-005 | UC-INT-001 — lảng vảng ngoài rào | Hành vi theo rule Cấp 4 (tối đa 5 phút) | Video 5 phút, ROI Xanh reference, alert log | BL-001 | Blocked |
| AC-INT-NEG-001 | UC-INT-NEG-001 — người ngoài ROI | Không phát sinh alert intrusion | Video, ROI snapshot reference | AS-002, BL-007 | Draft |
| AC-INT-NEG-002 | UC-INT-NEG-002/003/004 — ngoài object scope | Không alert nếu đối tượng ngoài object scope đã chốt | Video, ROI reference | BL-007 — `TBD_STAKEHOLDER_APPROVAL` | Blocked |

### 3.2. Camera cover / tamper

| ID | Use case | Điều kiện đạt | Evidence bắt buộc | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| AC-COV-001 | UC-COV-001 — che toàn phần | Alert cover đúng rule thời lượng tối thiểu | Video, alert log, timestamp, reviewer | BL-002 — `TBD_STAKEHOLDER_APPROVAL` | Blocked |
| AC-COV-002 | UC-COV-002 — che một phần | Alert/không alert theo ngưỡng % che đã chốt | Video, alert log, reviewer | BL-002 | Blocked |
| AC-COV-NEG-001 | UC-COV-NEG-001 — chói đèn xe | Không alert cover | Video, alert log | — | Draft |
| AC-COV-NEG-002 | UC-COV-NEG-002/003/004 — mưa, sương, thiếu sáng | Không alert cover, trừ khi rule phân loại là tamper | Video, alert log, annotation | BL-002 | Blocked |
| AC-COV-003 | UC-COV-EDGE-001/002/003 — freeze, black screen, video loss | Phân loại đúng tamper hoặc camera health theo rule đã chốt | Log, video | BL-005 — `TBD_STAKEHOLDER_APPROVAL` | Blocked |

### 3.3. Camera movement

| ID | Use case | Điều kiện đạt | Evidence bắt buộc | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| AC-MOV-001 | UC-MOV-001, UC-MOV-003 — lệch duy trì | Alert movement; phân biệt được rung ngắn và lệch duy trì | Before/after frame, movement score, alert log | BL-006 — `TBD_STAKEHOLDER_APPROVAL` | Blocked |
| AC-MOV-002 | UC-MOV-002 — `roi_drift` | Phát sinh alert movement hoặc camera-health event theo rule đã chốt | ROI snapshot before/after, video, log | BC-028, BL-006 | Blocked |
| AC-MOV-NEG-001 | UC-MOV-NEG-001 — rung ngắn rồi trở lại | Không alert movement theo duration rule | Video, movement data, alert log | BL-006 | Blocked |
| AC-MOV-NEG-002 | UC-MOV-NEG-002/003/004 — rung môi trường, scene change | Không alert movement | Video, alert log | — | Draft |

### 3.4. Data quality và traceability

> Use case `UC-DATA-001` … `UC-DATA-005` được bổ sung ngày 17/07/2026, chưa có trong `Use_Case_Catalogue_v0.1`. Định nghĩa đầy đủ nằm ở [`Requirement_Traceability_Matrix_v1.0.md`](./Requirement_Traceability_Matrix_v1.0.md) mục 4; nguồn requirement là Mục 2.2 (dòng "Data quality") và Mục 9 của kế hoạch.

| ID | Use case | Điều kiện đạt | Evidence bắt buộc | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| AC-DATA-001 | UC-DATA-001 — truy vết sample | Mỗi sample có `sample_id` duy nhất, không trùng | Manifest và annotation export | — | Draft |
| AC-DATA-002 | UC-DATA-002 — truy ngược nguồn | Mỗi sample truy được về `source_id`, `camera_id`, timestamp video nguồn | Manifest, inventory | — | Draft |
| AC-DATA-003 | UC-DATA-003 — ROI evidence | Sample phụ thuộc ROI có `roi_config_id`/`roi_version` và thời điểm hiệu lực | ROI snapshot reference | BC-036 | Draft |
| AC-DATA-004 | UC-DATA-004 — leakage | Test eligibility được ghi rõ: `Test eligible`/`Train overlap`/`Suspected overlap`/`Unknown` | `data_leakage_check_report` | AS-006, R-003 | Draft |
| AC-DATA-005 | UC-DATA-005 — ground truth độc lập | Candidate do tool sinh không được dùng làm nhãn cuối | Annotation export, reviewer | AS-003 | Draft |

### 3.5. E2E

| ID | Use case | Điều kiện đạt | Evidence bắt buộc | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| AC-E2E-001 | UC-E2E-001, UC-E2E-002 | Alert đúng camera, thời gian, loại và severity | Video, ROI evidence, alert/log | BL-008, BL-009 | Draft |
| AC-E2E-002 | UC-E2E-003 | Alert liên kết được tới `sample_id`/`source_id` và evidence | Clip, log, manifest reference | — | Draft |
| AC-E2E-003 | UC-E2E-004 | Không có alert trùng không kiểm soát; duplicate được ghi nhận riêng | Alert log, timestamp | BL-004 — `TBD_STAKEHOLDER_APPROVAL` | Blocked |
| AC-E2E-004 | UC-E2E-005 | Alert truy vết được về ROI config/version đang áp dụng | ROI snapshot/version reference | BC-036 | Draft |

## 4. Điều kiện loại khỏi KPI

Sample bị loại khỏi KPI chính thức khi:

- `ground_truth_status` là `ambiguous` hoặc `invalid`;
- video hỏng hoặc không đọc được;
- thiếu timestamp;
- thiếu ROI reference khi use case phụ thuộc ROI;
- chưa hoàn thành second review hoặc chưa adjudicate;
- `needs_second_review` chưa được khóa;
- test eligibility chưa xác định và use case yêu cầu tính độc lập với train data.

## 5. Quy tắc kết luận

| Trạng thái | Điều kiện |
|---|---|
| **Đạt** | Sample đã khóa/review; Precision ≥ 90%, Recall ≥ 90%, `FP/(TP+FP)` ≤ 10% cho nhóm tương ứng |
| **Không đạt** | Có đủ sample hợp lệ nhưng ít nhất một KPI không đạt |
| **Chưa kết luận** | Sample không đủ, train leakage chưa xác minh, hoặc còn nhiều case unresolved/ambiguous |
| **Rủi ro chấp nhận** | Stakeholder phê duyệt limitation kèm tác động và kế hoạch xử lý |

> Với trạng thái blocker hiện tại (BL-001 … BL-009 đều `Open`), kết luận KPI mặc định là **Chưa kết luận** cho cả ba nhóm.

## 6. Owner phê duyệt

| Hạng mục | Owner phê duyệt | Trạng thái |
|---|---|---|
| Acceptance criteria intrusion | Stakeholder | Chờ duyệt |
| Acceptance criteria cover/tamper | Stakeholder / AI Lead | Chờ duyệt |
| Acceptance criteria movement | AI Lead / Technical Owner | Chờ duyệt |
| Acceptance criteria data quality | QA Lead | Chờ duyệt |
| Acceptance criteria E2E | Product / Operations Owner | Chờ duyệt |
