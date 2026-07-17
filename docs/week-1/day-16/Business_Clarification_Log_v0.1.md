# Business Clarification Log v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Nguồn requirement:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 6 "Câu hỏi phải chốt trong Tuần 1"
> **Trạng thái tổng thể:** tất cả câu hỏi đang ở trạng thái `Open` hoặc `Blocked`. Chưa có câu trả lời nào được stakeholder xác nhận tại thời điểm phát hành v0.1.

## 1. Mục đích

Ghi nhận các câu hỏi nghiệp vụ, quyết định, assumption và blocker phục vụ thiết kế bộ dữ liệu kiểm thử AI Camera an ninh vành đai cho ba nhóm: trèo rào/xâm nhập, che camera/tamper và rung lắc/xoay lệch camera.

Tài liệu này là đầu vào bắt buộc để ngày 17/07/2026 khóa `Acceptance_Criteria_v1.0`, `Alert_Severity_and_Event_Rule_Spec_v1.0` và `Metric_and_KPI_Calculation_Rule_v1.0`.

## 2. Trạng thái

| Trạng thái | Ý nghĩa |
|---|---|
| `Open` | Đã hỏi, chưa có câu trả lời. |
| `Answered` | Đã có câu trả lời và owner phê duyệt xác nhận. |
| `Assumption` | Nhóm đang dùng giả định tạm thời, cần owner phê duyệt — xem [`Assumption_and_Blocker_Log_v0.1.md`](./Assumption_and_Blocker_Log_v0.1.md). |
| `Blocked` | Không thể tiếp tục công việc phụ thuộc nếu chưa có câu trả lời. |

## 3. Clarification log

### 3.1. Object scope

| ID | Nhóm | Câu hỏi | Câu trả lời | Status | Người trả lời | Người phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|---|---|---|
| BC-001 | Object scope | Model chỉ phát hiện người, hay gồm cả xe và động vật? | Chưa có | Open | AI Team | Stakeholder / AI Lead | 16/07/2026 | Không xác định được TP/FP cho `UC-INT-NEG-002` |
| BC-002 | Object scope | Nhân viên bảo vệ hoặc nhân viên nội bộ có được cảnh báo không? | Chưa có | Open | Operations | Stakeholder | 16/07/2026 | Có thể tính nhầm FP với hoạt động tuần tra hợp lệ |
| BC-003 | Object scope | Có whitelist người, phương tiện hoặc khung giờ không? | Chưa có | Open | Operations | Stakeholder | 16/07/2026 | Không mô hình hóa được negative hợp lệ |
| BC-004 | Object scope | Người xuất hiện hoàn toàn ngoài ROI có được tính là negative không? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | Nhãn `person_outside_roi` không khóa được; ảnh hưởng M2 |
| BC-005 | Object scope | Một phần cơ thể đi vào ROI có được tính là xâm nhập không? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | Sai TP/FN ở `UC-INT-005`, `UC-INT-006` |

### 3.2. Cấp độ cảnh báo (severity)

| ID | Nhóm | Câu hỏi | Câu trả lời | Status | Người trả lời | Người phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|---|---|---|
| BC-006 | Severity | ROI Xanh/Vàng/Đỏ tương ứng cấp cảnh báo nào? | Chưa có | Open | Operations | Stakeholder | 16/07/2026 | Không map được ROI → severity mong đợi |
| BC-007 | Severity | Cấp 2 và Cấp 3 khác nhau theo vị trí, thời lượng hay hành vi? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | Không gán severity nhất quán cho `person_approaching_fence` |
| BC-008 | Severity | Người tiếp cận hàng rào nhưng không chạm rào thuộc cấp nào? | Chưa có | Open | Stakeholder | Stakeholder | 16/07/2026 | Ranh giới Cấp 2/3/4 không xác định |
| BC-009 | Severity | Người trèo lên rồi quay xuống có phải Cấp 1 không? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | Sai nhãn `person_on_fence_top` và `UC-INT-EDGE-001` |
| BC-010 | Severity | Người đã đi vào khu vực cấm có luôn là Cấp 1 không? | Chưa có | Open | Stakeholder | Stakeholder | 16/07/2026 | Severity của `person_inside_restricted_area` chưa chốt |

### 3.3. Event boundary

| ID | Nhóm | Câu hỏi | Câu trả lời | Status | Người trả lời | Người phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|---|---|---|
| BC-011 | Event boundary | Event bắt đầu khi người xuất hiện, khi vào ROI hay khi bắt đầu hành vi? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | `event_start` không nhất quán giữa reviewer; sai latency |
| BC-012 | Event boundary | Event kết thúc khi người rời ROI hay sau một khoảng cooldown? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | `event_end` không nhất quán; ảnh hưởng đếm event |
| BC-013 | Event boundary | Một người đi Xanh → Vàng → Đỏ là một hay ba event? | Chưa có | Open | Product Owner | Operations Owner | 17/07/2026 | Không tính được duplicate alert (Mục 3.4 kế hoạch) |
| BC-014 | Event boundary | Hai người xuất hiện cùng lúc là một hay hai event? | Chưa có | Open | Stakeholder | Stakeholder | 16/07/2026 | Mẫu số TP/FN không xác định |
| BC-015 | Event boundary | Người rời ROI rồi quay lại sau bao lâu được tính event mới? | Chưa có | Open | Product Owner | Operations Owner | 17/07/2026 | Không có re-entry rule; duplicate vs event mới |
| BC-016 | Event boundary | Chỉ đưa tay hoặc chân vào ROI Đỏ có tính vượt rào không? | Chưa có | Blocked | Stakeholder | Stakeholder | 16/07/2026 | Sai TP/FN ở edge case ROI Đỏ |

### 3.4. Che camera / tamper

| ID | Nhóm | Câu hỏi | Câu trả lời | Status | Người trả lời | Người phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|---|---|---|
| BC-017 | Cover | Che bao nhiêu phần trăm khung hình thì tính là cover? | Chưa có | Blocked | AI Team | Stakeholder / AI Lead | 16/07/2026 | Không phân biệt `lens_full_cover` và `lens_partial_cover` |
| BC-018 | Cover | Phải che tối thiểu bao nhiêu giây? | Chưa có | Blocked | AI Team | Stakeholder / AI Lead | 16/07/2026 | Không khóa được duration rule cho `UC-COV-003` |
| BC-019 | Cover | Che một phần có alert không? | Chưa có | Open | AI Team | Stakeholder | 16/07/2026 | `lens_partial_cover` positive hay edge chưa rõ |
| BC-020 | Cover | Vật thể đi ngang lens trong thời gian ngắn có tính không? | Chưa có | Open | AI Team | Stakeholder | 16/07/2026 | `temporary_occlusion` positive hay negative chưa rõ |
| BC-021 | Cover | Mưa lớn có được tính là tamper không? | Chưa có | Open | Stakeholder | Stakeholder | 16/07/2026 | `rain_heavy` — hard negative hay camera health |
| BC-022 | Cover | Nước đọng hoặc sương mờ có tính là tamper không? | Chưa có | Open | Stakeholder | Stakeholder | 16/07/2026 | `water_drop_or_fog` chưa phân loại |
| BC-023 | Cover | Ánh đèn xe chiếu trực tiếp có tính là tamper không? | Chưa có | Open | AI Team | Stakeholder | 16/07/2026 | `headlight_glare` — ground truth không nhất quán |
| BC-024 | Cover | `black_screen`, `video_freeze`, `video_loss` thuộc tamper hay camera health? | Chưa có | Blocked | AI Team | Stakeholder / AI Lead | 16/07/2026 | Positive/negative bị lẫn; KPI cover sai mẫu số |

### 3.5. Camera movement

> Owner hỏi chính theo kế hoạch là B + C. A ghi nhận để thiết kế test boundary.

| ID | Nhóm | Câu hỏi | Câu trả lời | Status | Người trả lời | Người phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|---|---|---|
| BC-025 | Movement | Camera lệch bao nhiêu pixel hoặc bao nhiêu độ thì alert? | Chưa có | Blocked | AI Team | AI Lead / Technical Owner | 16/07/2026 | Không dựng được test boundary cho `sustained_camera_displacement` |
| BC-026 | Movement | Lệch trong bao nhiêu giây mới được tính positive? | Chưa có | Blocked | AI Team | AI Lead / Technical Owner | 16/07/2026 | Không phân biệt `temporary_shake` và displacement |
| BC-027 | Movement | Rung rồi trở lại vị trí cũ có alert không? | Chưa có | Open | AI Team | AI Lead | 16/07/2026 | `UC-MOV-NEG-001` chưa xác định expected result |
| BC-028 | Movement | ROI bị lệch khỏi vị trí vật lý có phải một loại lỗi riêng không? | Chưa có | Open | Product Owner | Technical Owner | 16/07/2026 | `roi_drift` — alert riêng hay camera health |
| BC-029 | Movement | Chuyển động của cây, xe hoặc ánh sáng có dễ bị nhầm thành camera movement không? | Chưa có | Open | AI Team | AI Lead | 16/07/2026 | Không biết cần bao nhiêu hard negative `scene_change_non_camera_move` |

### 3.6. KPI và SLA

> Theo kế hoạch, các mục này có hạn chốt ngày 17/07/2026; ngày 16 chỉ cần hỏi và ghi nhận.

| ID | Nhóm | Câu hỏi | Câu trả lời | Status | Người trả lời | Người phê duyệt | Hạn chốt | Tác động nếu chưa rõ |
|---|---|---|---|---|---|---|---|---|
| BC-030 | KPI | KPI tính theo event hay frame? | Chưa có — kế hoạch quy định tính theo event, cần stakeholder xác nhận | Assumption | QA Lead | Stakeholder / QA Lead | 17/07/2026 | Xem `AS-001` |
| BC-031 | KPI | Alert sai loại nhưng cùng khoảng thời gian tính FP + FN hay `misclassification`? | Chưa có | Blocked | QA / AI Team | Stakeholder / QA Lead | 17/07/2026 | KPI không nhất quán (Mục 3.4 kế hoạch) |
| BC-032 | Dedup | Nhiều alert cho một ground-truth event được tính thế nào? Cooldown bao lâu? | Chưa có — kế hoạch quy định một TP, phần còn lại là `duplicate_alert`; cần chốt cooldown | Open | Product Owner | Operations Owner | 17/07/2026 | Không tính được duplicate alert |
| BC-033 | SLA | Alert được phép chậm tối đa bao nhiêu giây cho Cấp 1 / cover / movement? | Chưa có | Open | Product Owner | Operations Owner | 17/07/2026 | Không đánh giá E2E được |
| BC-034 | SLA | Mốc tính latency bắt đầu từ event start hay từ lúc đối tượng vào ROI? | Chưa có | Open | Product Owner | Operations Owner | 17/07/2026 | Không so sánh được latency p50/p95 |
| BC-035 | KPI | M2 có giữ tên hiển thị "tỷ lệ báo động giả" không, hay đổi để tránh nhầm với `FP/(FP+TN)`? | Chưa có | Open | QA Lead | Stakeholder | 17/07/2026 | Nhầm lẫn khi báo cáo (Mục 3.3 kế hoạch) |

### 3.7. Câu hỏi liên quan do A ghi nhận hộ owner khác

| ID | Nhóm | Câu hỏi | Owner hỏi | Status | Hạn chốt | Ghi chú |
|---|---|---|---|---|---|---|
| BC-036 | ROI evidence | Tool cung cấp `roi_config_id`, `roi_version`, snapshot và thời điểm hiệu lực như thế nào? | B | Open | 16/07/2026 | Không hỏi tạo/thay đổi ROI — ngoài phạm vi |
| BC-037 | Data leakage | AI team có train manifest, checksum, source list hoặc danh sách camera/ngày train không? | B | Open | 16/07/2026 | Nếu không có, eligibility phải là `Unknown` |
| BC-038 | Ground truth | Ai quan sát hiện trường, nguồn nào là chuẩn, ai adjudicate case bất đồng? | C | Open | 17/07/2026 | Ảnh hưởng khóa nhãn cuối |
| BC-039 | PII/storage | Chính sách lưu video/mặt/biển số, quyền truy cập và thời hạn lưu là gì? | B + C | Open | 17/07/2026 | Rủi ro tuân thủ khi bàn giao |

## 4. Tổng hợp trạng thái

| Status | Số lượng | ID |
|---|---:|---|
| `Open` | 25 | BC-001, BC-002, BC-003, BC-006, BC-008, BC-010, BC-013, BC-014, BC-015, BC-019, BC-020, BC-021, BC-022, BC-023, BC-027, BC-028, BC-029, BC-032, BC-033, BC-034, BC-035, BC-036, BC-037, BC-038, BC-039 |
| `Blocked` | 13 | BC-004, BC-005, BC-007, BC-009, BC-011, BC-012, BC-016, BC-017, BC-018, BC-024, BC-025, BC-026, BC-031 |
| `Assumption` | 1 | BC-030 |
| `Answered` | 0 | — |

> Không có câu hỏi nào ở trạng thái `Answered` tại thời điểm phát hành v0.1. Mọi công việc phụ thuộc (khóa acceptance criteria, khóa guideline nhãn, tính KPI) phải chờ hoặc chạy dưới dạng dry-run.

## 5. Quy tắc sử dụng

- Không tự suy diễn câu trả lời nghiệp vụ. Không có câu trả lời thì trạng thái phải là `Open`, `Assumption` hoặc `Blocked`.
- Mọi assumption phải có owner phê duyệt và hạn xác nhận.
- Câu trả lời miệng cần ghi rõ người xác nhận và ngày xác nhận trước khi chuyển sang `Answered`.
- Câu hỏi `Blocked` phải có impact và phương án fallback trong [`Assumption_and_Blocker_Log_v0.1.md`](./Assumption_and_Blocker_Log_v0.1.md).
- Candidate do pipeline mining sinh ra chỉ là dữ liệu gợi ý để con người review, **không phải ground truth** và không được dùng để trả lời các câu hỏi trong log này.
