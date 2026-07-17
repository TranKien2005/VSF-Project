# Requirement Traceability Matrix v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Thay thế:** [`Requirement_Traceability_Matrix_v0.1`](../day-16/Requirement_Traceability_Matrix_v0.1.md) (ngày 16)
> **Chuỗi truy vết:** `Requirement → Use case → Test category → Evidence → KPI`

## 0. Trạng thái

Toàn bộ requirement ở trạng thái `Draft`. Không requirement nào được `Locked` vì các blocker BL-001 … BL-009 vẫn `Open`. Cột "Acceptance" trỏ tới [`Acceptance_Criteria_v1.0.md`](./Acceptance_Criteria_v1.0.md).

Thay đổi so với v0.1: bổ sung cột Owner và Acceptance, thêm nhóm requirement `REQ-DATA-*`, gộp một số requirement intrusion để bám sát acceptance criteria.

## 1. Intrusion

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Acceptance | Owner | Blocker | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-INT-001 | Phát hiện người trèo rào | UC-INT-004, UC-INT-005 | Positive | Video + alert log + ROI reference + timestamp | M1, M3 | AC-INT-001 | A/C | BL-003 | Draft |
| REQ-INT-002 | Phát hiện người vượt rào và cảnh báo Cấp 1 | UC-INT-006 | Critical positive | Video + alert log + ROI Đỏ reference | M1, latency | AC-INT-002 | A/C | BL-003, BL-009 | Draft |
| REQ-INT-003 | Phát hiện người trong khu vực cấm và cảnh báo Cấp 1 | UC-INT-007 | Critical positive | Video + alert log + ROI reference | M1, latency | AC-INT-003 | A/C | BL-009 | Draft |
| REQ-INT-004 | Gán đúng severity cho tiếp cận/chạm rào | UC-INT-002, UC-INT-003 | Positive | Video + alert log + ROI reference | M3 | AC-INT-004 | A | BL-001 | Draft |
| REQ-INT-005 | Xử lý lảng vảng ngoài rào theo rule Cấp 4 | UC-INT-001 | Edge/positive | Video 5 phút + ROI Xanh reference + alert log | M1, M3 | AC-INT-005 | A | BL-001 | Draft |
| REQ-INT-006 | Không báo intrusion với người ngoài ROI | UC-INT-NEG-001 | Hard negative | Video + ROI snapshot reference | M2 | AC-INT-NEG-001 | A/C | BL-007 | Draft |
| REQ-INT-007 | Không báo với đối tượng ngoài object scope | UC-INT-NEG-002, UC-INT-NEG-003, UC-INT-NEG-004 | Negative/hard negative | Video + ROI reference | M2 | AC-INT-NEG-002 | A/C | BL-007 | Draft |
| REQ-INT-008 | Xử lý nhất quán edge case trèo/quay xuống và một phần cơ thể vào ROI | UC-INT-EDGE-001, UC-INT-EDGE-002 | Edge | Video + event boundary + alert log | M1, M2 | AC-INT-001 | A/C | BL-003 | Draft |
| REQ-INT-009 | Đếm event nhất quán khi chuyển cấp hoặc nhiều đối tượng | UC-INT-EDGE-003, UC-INT-EDGE-004, UC-INT-EDGE-005 | Edge/dedup | Video + alert log + timestamp | M1, duplicate rate | AC-E2E-003 | A/B | BL-004 | Draft |

## 2. Camera cover / tamper

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Acceptance | Owner | Blocker | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-COV-001 | Phát hiện che toàn phần lens | UC-COV-001 | Positive | Video + alert log + timestamp | M1, M3 | AC-COV-001 | A/C | BL-002 | Draft |
| REQ-COV-002 | Xử lý che một phần theo ngưỡng % và thời lượng | UC-COV-002, UC-COV-003 | Edge/positive | Video + alert log + annotation | M1, M3 | AC-COV-002 | A/C | BL-002 | Draft |
| REQ-COV-003 | Không nhầm chói đèn xe thành che | UC-COV-NEG-001 | Hard negative | Video + annotation + alert log | M2 | AC-COV-NEG-001 | A/C | — | Draft |
| REQ-COV-004 | Không nhầm mưa, sương, thiếu sáng thành che | UC-COV-NEG-002, UC-COV-NEG-003, UC-COV-NEG-004 | Hard negative | Video + annotation + alert log | M2 | AC-COV-NEG-002 | A/C | BL-002 | Draft |
| REQ-COV-005 | Không nhầm vật che tạm thời thành che | UC-COV-NEG-005 | Hard negative | Video + alert log | M2 | AC-COV-002 | A/C | BL-002 | Draft |
| REQ-COV-006 | Phân loại đúng freeze/black screen/video loss | UC-COV-EDGE-001, UC-COV-EDGE-002, UC-COV-EDGE-003 | Edge/camera health | Log + video | Tách khỏi KPI cover cho tới khi chốt | AC-COV-003 | A/B | BL-005 | Draft |

## 3. Camera movement

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Acceptance | Owner | Blocker | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-MOV-001 | Phát hiện camera lệch/xoay duy trì | UC-MOV-001, UC-MOV-003 | Positive | Before/after frame + movement data + alert log | M1, M3 | AC-MOV-001 | A/B | BL-006 | Draft |
| REQ-MOV-002 | Phát hiện `roi_drift` | UC-MOV-002 | Positive | ROI snapshot before/after + video + log | M1 | AC-MOV-002 | A/B | BL-006 | Draft |
| REQ-MOV-003 | Không nhầm rung ngắn thành lệch duy trì | UC-MOV-NEG-001 | Hard negative | Video + movement data + alert log | M2 | AC-MOV-NEG-001 | A/B/C | BL-006 | Draft |
| REQ-MOV-004 | Không nhầm rung môi trường thành movement | UC-MOV-NEG-002 | Hard negative | Video + alert log | M2 | AC-MOV-NEG-002 | A/B/C | BL-006 | Draft |
| REQ-MOV-005 | Không nhầm scene change thành movement | UC-MOV-NEG-003, UC-MOV-NEG-004 | Hard negative | Video + annotation | M2 | AC-MOV-NEG-002 | A/B/C | — | Draft |

## 4. Data quality và traceability

> Use case `UC-DATA-001` … `UC-DATA-005` được định nghĩa lần đầu ở đây (ngày 17), bổ sung cho `Use_Case_Catalogue_v0.1`. Nguồn requirement: Mục 2.2 (dòng "Data quality") và Mục 9 của kế hoạch, cùng data contract trong README.

| Use case ID | Định nghĩa |
|---|---|
| UC-DATA-001 | Mỗi sample có `sample_id` duy nhất trong toàn bộ manifest và annotation export |
| UC-DATA-002 | Mỗi sample truy ngược được về `source_id`, `camera_id` và timestamp trong video nguồn |
| UC-DATA-003 | Sample phụ thuộc ROI có `roi_config_id`/`roi_version`, thời điểm hiệu lực và snapshot reference |
| UC-DATA-004 | Mỗi sample có test eligibility rõ ràng: `Test eligible`, `Train overlap`, `Suspected overlap` hoặc `Unknown` |
| UC-DATA-005 | Ground truth do con người review; output candidate mining không được dùng làm nhãn cuối |

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Acceptance | Owner | Blocker | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-DATA-001 | Sample truy vết được bằng `sample_id` duy nhất | UC-DATA-001 | Data quality | Manifest + annotation export | N/A — điều kiện để KPI hợp lệ | AC-DATA-001 | B | — | Draft |
| REQ-DATA-002 | Sample truy ngược được về video nguồn và camera | UC-DATA-002 | Data quality | Manifest + inventory | N/A | AC-DATA-002 | B | — | Draft |
| REQ-DATA-003 | ROI reference đầy đủ cho use case phụ thuộc ROI | UC-DATA-003 | Data quality | ROI snapshot/version reference | N/A | AC-DATA-003 | B | BC-036 | Draft |
| REQ-DATA-004 | Test eligibility được báo cáo, không tuyên bố độc lập khi thiếu train manifest | UC-DATA-004 | Data quality | `data_leakage_check_report` | N/A | AC-DATA-004 | B | R-003 | Draft |
| REQ-DATA-005 | Candidate mining không được dùng làm ground truth | UC-DATA-005 | Data quality | Annotation export + reviewer | N/A | AC-DATA-005 | C | — | Draft |

## 5. E2E

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Acceptance | Owner | Blocker | Status |
|---|---|---|---|---|---|---|---|---|---|
| REQ-E2E-001 | Alert đúng camera và timestamp | UC-E2E-001 | E2E | Alert log + video + timestamp | Latency p50/p95 | AC-E2E-001 | A/B | BL-009 | Draft |
| REQ-E2E-002 | Alert đúng loại sự kiện và severity | UC-E2E-002 | E2E | Alert log + ground truth | M3, misclassification | AC-E2E-001 | A/B | BL-008 | Draft |
| REQ-E2E-003 | Alert/sample có evidence truy vết đầy đủ | UC-E2E-003 | E2E | Clip + log + manifest reference | Điều kiện để KPI hợp lệ | AC-E2E-002 | A/B | — | Draft |
| REQ-E2E-004 | Không có alert trùng không kiểm soát | UC-E2E-004 | E2E/dedup | Alert log + timestamp | Duplicate rate | AC-E2E-003 | A/B | BL-004 | Draft |
| REQ-E2E-005 | Alert truy vết được về ROI config/version | UC-E2E-005 | E2E | ROI snapshot/version reference | Điều kiện để KPI hợp lệ | AC-E2E-004 | A/B | BC-036 | Draft |

## 6. Coverage tự kiểm

| Nhóm bắt buộc | Positive | Negative / hard negative | Edge case | Truy tới KPI | Truy tới Acceptance |
|---|---|---|---|---|---|
| Trèo rào/xâm nhập | REQ-INT-001 … 005 | REQ-INT-006, 007 | REQ-INT-008, 009 | Có | Có |
| Che camera/tamper | REQ-COV-001, 002 | REQ-COV-003, 004, 005 | REQ-COV-006 | Có | Có |
| Camera movement | REQ-MOV-001, 002 | REQ-MOV-003, 004, 005 | REQ-MOV-003 | Có | Có |
| Data quality | — | — | — | Điều kiện hợp lệ | Có |
| E2E | REQ-E2E-001 … 005 | — | REQ-E2E-004 | Có | Có |

Tổng: 30 requirement, 100% có use case, test category, evidence, KPI hoặc lý do `N/A`, và acceptance criteria tương ứng.

## 7. Ghi chú

- Candidate do pipeline mining sinh ra không được dùng làm evidence ground truth cho bất kỳ requirement nào.
- Requirement chuyển sang `Locked` chỉ khi blocker liên quan đóng hoặc assumption được stakeholder chấp nhận bằng văn bản.
