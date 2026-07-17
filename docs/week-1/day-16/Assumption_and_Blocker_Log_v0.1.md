# Assumption and Blocker Log v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Liên kết:** [`Business_Clarification_Log_v0.1.md`](./Business_Clarification_Log_v0.1.md)

## 1. Assumptions

Assumption là giả định tạm thời để nhóm tiếp tục công việc thiết kế. Assumption **không phải là câu trả lời nghiệp vụ** và phải được owner phê duyệt trước khi dùng để khóa ground truth hoặc KPI.

| ID | Assumption | Lý do | Impact nếu sai | Owner phê duyệt | Hạn xác nhận | Status |
|---|---|---|---|---|---|---|
| AS-001 | KPI tính theo event, không theo frame | Mục 3.4 kế hoạch quy định như vậy, nhưng chưa có xác nhận của stakeholder | Ảnh hưởng toàn bộ metric M1/M2/M3 và mẫu số TP/FP/FN | Stakeholder / QA Lead | 17/07/2026 | Open |
| AS-002 | Người hoàn toàn ngoài ROI là negative | Chưa có whitelist rule và chưa chốt object scope | Có thể tính nhầm FP; ảnh hưởng `UC-INT-NEG-001` | Stakeholder | 16/07/2026 | Open |
| AS-003 | Candidate mining không tạo ground truth; ground truth cần human review | Mục 2.1 kế hoạch và README quy định | Label leakage và automation bias nếu làm khác | QA Lead | 16/07/2026 | Open |
| AS-004 | Một ground-truth event có nhiều alert chỉ tính một TP; phần còn lại là `duplicate_alert` | Mục 3.4 kế hoạch; cooldown cụ thể chưa có | Sai số đếm TP và tỷ lệ alert trùng | Product Owner / Operations Owner | 17/07/2026 | Open |
| AS-005 | `ambiguous` và `invalid` không đưa vào KPI chính thức và không vào golden set | Mục 3.4 và 4.4 kế hoạch | KPI bị nhiễu bởi case không kết luận được | QA Lead | 17/07/2026 | Open |
| AS-006 | Test eligibility là `Unknown` cho tới khi AI team cung cấp train manifest | Mục 9.1 kế hoạch | Không được tuyên bố test set độc lập với train data | B / AI Team | 16/07/2026 | Open |
| AS-007 | ROI hiện có được dùng nguyên trạng; không tạo hoặc thay đổi ROI | Mục 1.1 kế hoạch — ngoài phạm vi | Test nhầm giữa các phiên bản ROI | Technical Owner | 16/07/2026 | Open |

## 2. Blockers

| ID | Blocker | Impact | Owner xử lý | Fallback | Clarification | Status |
|---|---|---|---|---|---|---|
| BL-001 | Chưa có định nghĩa phân biệt Cấp 2 và Cấp 3 ở ROI Vàng | Không gán severity nhất quán cho `person_approaching_fence` | Stakeholder | Đánh dấu `needs_second_review`; không khóa severity | BC-007 | Open |
| BL-002 | Chưa có cover threshold (% che và thời lượng tối thiểu) | Không phân biệt positive/negative cho `lens_partial_cover` và `temporary_occlusion` | AI Lead | Không khóa ground truth nhóm cover; chỉ ghi nhận quan sát | BC-017, BC-018 | Open |
| BL-003 | Chưa có event boundary (start/end, một phần cơ thể vào ROI, trèo rồi quay xuống) | Không tính TP/FN chính xác; `event_start`/`event_end` không nhất quán giữa reviewer | Stakeholder | Chỉ thực hiện dry-run; không tính KPI chính thức | BC-005, BC-009, BC-011, BC-012, BC-016 | Open |
| BL-004 | Chưa có cooldown/dedup rule và re-entry rule | Không tính được duplicate alert và số event | Product Owner | Báo cáo `duplicate_alert` riêng, không cộng vào TP | BC-013, BC-015, BC-032 | Open |
| BL-005 | Chưa chốt `black_screen`/`video_freeze`/`video_loss` là tamper hay camera health | Ground truth nhóm cover không nhất quán; sai mẫu số KPI | AI Lead / Stakeholder | Gán nhãn riêng camera health, tách khỏi KPI cover | BC-024 | Open |
| BL-006 | Chưa có ngưỡng movement (pixel/độ) và thời lượng tối thiểu | Không dựng được test boundary giữa `temporary_shake` và `sustained_camera_displacement` | AI Lead / Technical Owner | Ghi nhận before/after frame; không khóa nhãn movement | BC-025, BC-026 | Open |
| BL-007 | Chưa chốt object scope (người/xe/động vật/nhân viên, whitelist) | Không xác định TP/FP cho `UC-INT-NEG-002`, `UC-INT-NEG-003`, `UC-INT-NEG-004` | Stakeholder / AI Lead | Gán `ambiguous` cho case ngoài phạm vi người | BC-001, BC-002, BC-003 | Open |
| BL-008 | Chưa chốt alert sai loại tính FP+FN hay `misclassification` | KPI không nhất quán giữa ba nhóm | Stakeholder / QA Lead | Báo cáo cả hai cách tính kèm ghi chú, chưa kết luận | BC-031 | Open |
| BL-009 | Chưa có detection window và mốc tính latency | Không xác định được TP trong "cửa sổ thời gian đã thống nhất"; không đánh giá E2E | Product Owner / Operations Owner | Ghi latency thô, đánh dấu `Chưa kết luận` | BC-033, BC-034 | Open |

## 3. Ảnh hưởng tới tiến độ

| Hạng mục ngày 17/07/2026 | Phụ thuộc blocker | Rủi ro |
|---|---|---|
| `Acceptance_Criteria_v1.0` | BL-001, BL-003, BL-007 | Không khóa được pass/fail theo severity |
| `Alert_Severity_and_Event_Rule_Spec_v1.0` | BL-001, BL-003, BL-004 | Không mô tả được state transition và cooldown |
| `Metric_and_KPI_Calculation_Rule_v1.0` | BL-004, BL-008, BL-009 | Không khóa được quy tắc đếm TP/FP/FN |
| `Requirement_Traceability_Matrix_v1.0` | BL-002, BL-005, BL-006 | Requirement nhóm cover/movement còn ở `Draft` |

## 4. Quy tắc

- Blocker chưa giải quyết phải ghi rõ impact và fallback; **không tự diễn giải requirement** (Mục 7, ngày 17 của kế hoạch).
- Assumption chuyển sang `Answered` chỉ khi owner phê duyệt xác nhận, kèm tên người và ngày xác nhận.
- Gate kết thúc Tuần 1 chỉ được mở khi các blocker BL-001, BL-002, BL-003, BL-006 có định nghĩa đủ để gán nhãn, hoặc assumption thay thế đã được stakeholder chấp nhận.
