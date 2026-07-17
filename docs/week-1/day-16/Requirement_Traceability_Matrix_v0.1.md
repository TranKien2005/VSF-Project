# Requirement Traceability Matrix v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Trạng thái:** bản nháp. Toàn bộ requirement ở trạng thái `Draft` cho tới khi clarification tương ứng được `Answered`. Bản `v1.0` được khóa vào ngày 17/07/2026.

Chuỗi truy vết: `Requirement → Use case → Test category → Evidence → KPI`.

## 1. Intrusion

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Blocker | Status |
|---|---|---|---|---|---|---|---|
| REQ-INT-001 | Phát hiện người lảng vảng ngoài hàng rào theo rule Cấp 4 | UC-INT-001 | Edge/positive | Video 5 phút + ROI reference + alert log | M1, M3 | BL-001 | Draft |
| REQ-INT-002 | Phát hiện người tiếp cận sát hàng rào | UC-INT-002 | Positive | Video + ROI reference + alert log | M1, M3 | BL-001 | Draft |
| REQ-INT-003 | Phát hiện người chạm/bám hàng rào | UC-INT-003 | Positive | Video + ROI reference + alert log | M1, M3 | BL-001 | Draft |
| REQ-INT-004 | Phát hiện người trèo rào | UC-INT-004, UC-INT-005 | Positive | Video + timestamp + alert log | M1, M3 | BL-003 | Draft |
| REQ-INT-005 | Phát hiện người vượt rào và cảnh báo Cấp 1 | UC-INT-006 | Critical positive | Video + ROI Đỏ reference + alert log | M1, latency | BL-003, BL-009 | Draft |
| REQ-INT-006 | Phát hiện người trong khu vực cấm và cảnh báo Cấp 1 | UC-INT-007 | Critical positive | Video + ROI reference + alert log | M1, latency | BL-009 | Draft |
| REQ-INT-007 | Không báo intrusion với người hoàn toàn ngoài ROI | UC-INT-NEG-001 | Hard negative | Video + ROI reference | M2, M3 | BL-007 | Draft |
| REQ-INT-008 | Không báo intrusion với đối tượng ngoài object scope | UC-INT-NEG-002, UC-INT-NEG-003, UC-INT-NEG-004 | Negative/hard negative | Video + ROI reference | M2, M3 | BL-007 | Draft |
| REQ-INT-009 | Xử lý nhất quán các edge case trèo/quay xuống và một phần cơ thể vào ROI | UC-INT-EDGE-001, UC-INT-EDGE-002 | Edge | Video + event boundary + alert log | M1, M2 | BL-003 | Draft |
| REQ-INT-010 | Đếm event nhất quán khi chuyển cấp hoặc nhiều đối tượng | UC-INT-EDGE-003, UC-INT-EDGE-004, UC-INT-EDGE-005 | Edge/dedup | Video + alert log + timestamp | M1, tỷ lệ alert trùng | BL-004 | Draft |

## 2. Camera cover / tamper

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Blocker | Status |
|---|---|---|---|---|---|---|---|
| REQ-COV-001 | Phát hiện che gần/toàn bộ lens đủ thời lượng | UC-COV-001 | Positive | Video + alert log + timestamp | M1, M3 | BL-002 | Draft |
| REQ-COV-002 | Xử lý che một phần lens theo ngưỡng đã chốt | UC-COV-002, UC-COV-003 | Edge/positive | Video + alert log | M1, M3 | BL-002 | Draft |
| REQ-COV-003 | Không nhầm ánh đèn xe thành cover | UC-COV-NEG-001 | Hard negative | Video + alert log | M2 | — | Draft |
| REQ-COV-004 | Không nhầm nhiễu môi trường (mưa, sương, thiếu sáng) thành cover | UC-COV-NEG-002, UC-COV-NEG-003, UC-COV-NEG-004 | Hard negative | Video + alert log | M2 | BL-002 | Draft |
| REQ-COV-005 | Không nhầm vật thể che tạm thời thành cover | UC-COV-NEG-005 | Hard negative | Video + alert log | M2 | BL-002 | Draft |
| REQ-COV-006 | Phân loại đúng black screen / freeze / video loss là tamper hay camera health | UC-COV-EDGE-001, UC-COV-EDGE-002, UC-COV-EDGE-003 | Edge/camera health | Log + video | Không tính KPI cover cho tới khi chốt | BL-005 | Draft |

## 3. Camera movement

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Blocker | Status |
|---|---|---|---|---|---|---|---|
| REQ-MOV-001 | Phát hiện camera lệch/xoay hướng duy trì | UC-MOV-001, UC-MOV-003 | Positive | Before/after frame + alert log | M1, M3 | BL-006 | Draft |
| REQ-MOV-002 | Phát hiện `roi_drift` khi góc camera lệch khỏi vùng vật lý | UC-MOV-002 | Positive | ROI snapshot before/after + video | M1 | BL-006 | Draft |
| REQ-MOV-003 | Không nhầm rung ngắn rồi trở lại thành movement | UC-MOV-NEG-001 | Hard negative/edge | Video + alert log | M2 | BL-006 | Draft |
| REQ-MOV-004 | Không nhầm rung môi trường thành movement | UC-MOV-NEG-002 | Hard negative | Video + alert log | M2 | BL-006 | Draft |
| REQ-MOV-005 | Không nhầm scene change (cây, vật thể, ánh sáng) thành movement | UC-MOV-NEG-003, UC-MOV-NEG-004 | Hard negative | Video | M2 | — | Draft |

## 4. E2E tối thiểu

| Requirement ID | Requirement | Use case | Test category | Evidence | KPI | Blocker | Status |
|---|---|---|---|---|---|---|---|
| REQ-E2E-001 | Alert gắn đúng camera và timestamp | UC-E2E-001 | E2E | Video + timestamp + alert log | Latency p50/p95 | BL-009 | Draft |
| REQ-E2E-002 | Alert đúng loại sự kiện và cấp độ | UC-E2E-002 | E2E | Alert log + ground truth | M3, misclassification | BL-008 | Draft |
| REQ-E2E-003 | Mọi alert/sample truy vết được về video nguồn và reviewer | UC-E2E-003 | E2E | Clip + log + manifest reference | Điều kiện để KPI hợp lệ | — | Draft |
| REQ-E2E-004 | Không có alert trùng không kiểm soát cho một event | UC-E2E-004 | E2E/dedup | Alert log + timestamp | Tỷ lệ alert trùng | BL-004 | Draft |
| REQ-E2E-005 | Alert truy vết được về ROI config/version đang áp dụng | UC-E2E-005 | E2E | ROI snapshot/version reference | Điều kiện để KPI hợp lệ | BC-036 | Draft |

## 5. Coverage tự kiểm

| Nhóm bắt buộc | Có positive | Có negative/hard negative | Có edge case | Có traceability tới KPI |
|---|---|---|---|---|
| Trèo rào/xâm nhập | Có (REQ-INT-001…006) | Có (REQ-INT-007, 008) | Có (REQ-INT-009, 010) | Có |
| Che camera/tamper | Có (REQ-COV-001, 002) | Có (REQ-COV-003, 004, 005) | Có (REQ-COV-006) | Có |
| Camera movement | Có (REQ-MOV-001, 002) | Có (REQ-MOV-003, 004, 005) | Có (REQ-MOV-003) | Có |
| E2E tối thiểu | Có (REQ-E2E-001…005) | — | — | Có |

## 6. Ghi chú

- Không có requirement nào ở trạng thái `Locked`; `v1.0` chỉ được khóa sau khi các blocker liên quan được giải quyết hoặc assumption được stakeholder chấp nhận.
- Candidate do pipeline mining sinh ra không được dùng làm evidence ground truth cho bất kỳ requirement nào trong bảng này.
