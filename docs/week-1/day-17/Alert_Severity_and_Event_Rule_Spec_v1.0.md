# Alert Severity and Event Rule Specification v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Reviewer:** C (taxonomy, event boundary, ambiguous), B (log/alert correlation), Stakeholder (phê duyệt)
> **Nguồn requirement:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 1.1, 3.4, 4

## 0. Trạng thái phát hành

```text
Status: ASSUMPTION
Approval required from: Mentor/Stakeholder, Operations Owner, AI Lead
Impact: KPI chưa được coi là kết quả chính thức
Fallback: Áp dụng rule tạm thời để dry-run, không khóa golden set
```

Các mục đánh dấu `TBD_STAKEHOLDER_APPROVAL` là điểm chưa có câu trả lời nghiệp vụ. **Không suy diễn** — xem [`Business_Clarification_Log_v0.1`](../day-16/Business_Clarification_Log_v0.1.md).

## 1. Severity

| Cấp | Ý nghĩa | Ví dụ nhãn | ROI dự kiến | Trạng thái |
|---|---|---|---|---|
| Cấp 1 | Khẩn cấp | `person_crossing_fence`, `person_inside_restricted_area` | ROI Đỏ | ASSUMPTION — theo Mục 4.1 kế hoạch |
| Cấp 2 | Nguy cơ cao | `person_approaching_fence`, `person_touching_fence` | ROI Vàng/Đỏ | `TBD_STAKEHOLDER_APPROVAL` (BC-007, BL-001) |
| Cấp 3 | Cần theo dõi | `person_approaching_fence` | ROI Vàng | `TBD_STAKEHOLDER_APPROVAL` (BC-007, BL-001) |
| Cấp 4 | Theo dõi | `person_near_fence` — lảng vảng vùng ngoài, tối đa 5 phút | ROI Xanh | ASSUMPTION — theo Mục 4.1 kế hoạch |

> **Điều kiện phân biệt Cấp 2 và Cấp 3 chưa được cung cấp.** Kế hoạch chỉ ghi "Cấp 2 hoặc 3 — cần chốt rule phân biệt". Không tự chọn tiêu chí thời lượng, vị trí hay hành vi khi chưa có stakeholder xác nhận (BL-001).

### 1.1. Severity của các case chưa chốt

| Case | Severity | Trạng thái |
|---|---|---|
| `person_on_fence_top` — người ở đỉnh rào | Ứng viên Cấp 1 | `TBD_STAKEHOLDER_APPROVAL` (BC-009) |
| `person_climbing_fence` — trèo rồi quay xuống phía ngoài | Chưa xác định | `TBD_STAKEHOLDER_APPROVAL` (BC-009) |
| Một phần cơ thể (tay/chân) vào ROI Đỏ | Chưa xác định — có tính vượt rào không | `TBD_STAKEHOLDER_APPROVAL` (BC-005, BC-016) |
| Người tiếp cận rào nhưng không chạm | Chưa xác định — Cấp 2, 3 hay 4 | `TBD_STAKEHOLDER_APPROVAL` (BC-008) |
| `roi_drift` | Alert movement hay camera health riêng | `TBD_STAKEHOLDER_APPROVAL` (BC-028) |
| `black_screen`, `video_freeze`, `video_loss` | Tamper hay camera health | `TBD_STAKEHOLDER_APPROVAL` (BC-024, BL-005) |

## 2. Event boundary

Mỗi ground-truth event phải có tối thiểu:

```text
event_id
sample_id
source_id
camera_id
roi_config_id
roi_version
event_label
event_start_sec
event_end_sec
severity
ground_truth_status
reviewer
review_timestamp
```

- `event_start_sec` và `event_end_sec` tính theo giây từ đầu **video nguồn** (theo data contract trong README).
- Ràng buộc bắt buộc: `event_start_sec < event_end_sec`.

### 2.1. Quy tắc start/end — chưa khóa

| Câu hỏi | Trạng thái | ID |
|---|---|---|
| Event bắt đầu khi người xuất hiện, khi vào ROI hay khi bắt đầu hành vi? | `TBD_STAKEHOLDER_APPROVAL` | BC-011, BL-003 |
| Event kết thúc khi người rời ROI hay sau cooldown? | `TBD_STAKEHOLDER_APPROVAL` | BC-012, BL-003 |
| Hai người xuất hiện cùng lúc là một hay hai event? | `TBD_STAKEHOLDER_APPROVAL` | BC-014 |
| Người rời ROI rồi quay lại sau bao lâu là event mới? | `TBD_STAKEHOLDER_APPROVAL` | BC-015 |

**Fallback dry-run** (không dùng để khóa ground truth): reviewer ghi `event_start_sec` tại thời điểm đối tượng bắt đầu hành vi quan sát được và `event_end_sec` tại thời điểm hành vi kết thúc trong khung hình; mọi bất đồng đưa vào `needs_second_review`. Rule này **không phải quyết định nghiệp vụ** và phải thay bằng câu trả lời chính thức trước khi tính KPI.

## 3. State transition

```text
person_near_fence            (ROI Xanh — Cấp 4)
  → person_approaching_fence (ROI Vàng — Cấp 2 hoặc 3: TBD)
  → person_touching_fence    (ROI Vàng/Đỏ tùy ROI thực tế)
  → person_climbing_fence    (Cấp: TBD theo event boundary)
  → person_on_fence_top      (Ứng viên Cấp 1: TBD)
  → person_crossing_fence    (ROI Đỏ — Cấp 1)
  → person_inside_restricted_area (ROI Đỏ — Cấp 1)
```

Ghi chú:

- Chuỗi trên là **thứ tự leo thang điển hình**, không bắt buộc đối tượng đi qua đủ các trạng thái.
- Đối tượng có thể thoát khỏi chuỗi ở bất kỳ trạng thái nào (ví dụ trèo rồi quay xuống — BC-009).
- `person_outside_roi` không thuộc chuỗi; là negative/hard negative.
- **Xanh → Vàng → Đỏ là một incident cập nhật hay nhiều alert riêng: `TBD_STAKEHOLDER_APPROVAL`** (BC-013, BL-004).

## 4. Dedup rule

- Một ground-truth event chỉ được ghép tối đa **một TP**.
- Các alert còn lại trong cùng incident ghi là `duplicate_alert`.
- Không tự động tính `duplicate_alert` thành TP; báo cáo riêng như metric bổ sung.
- **Cooldown:** `TBD_STAKEHOLDER_APPROVAL` (BC-032, BL-004).
- **Incident merge gap:** `TBD_STAKEHOLDER_APPROVAL` (BC-032, BL-004).
- **Re-entry threshold** (rời ROI rồi quay lại): `TBD_STAKEHOLDER_APPROVAL` (BC-015).

Ba quy tắc đầu tiên có nguồn trực tiếp từ Mục 3.4 của kế hoạch; ba giá trị ngưỡng còn lại chưa có.

## 5. Uncertain cases

| Trạng thái | Ý nghĩa | Tính KPI |
|---|---|---|
| `confirmed_positive` | Đã review, có event | Có |
| `confirmed_negative` | Đã review, không có event | Có |
| `needs_second_review` | Chưa được khóa ground truth | Không |
| `ambiguous` | Không thể kết luận theo guideline | Không — lưu để cải thiện guideline |
| `invalid` | Dữ liệu không hợp lệ | Không — lưu để cải thiện guideline |

- `ambiguous` và `invalid` không đưa vào golden set.
- Clip thiếu context hoặc không thể kết luận phải gán `ambiguous`/`invalid`, **không ép thành positive/negative**.

## 6. Detection window và latency

| Hạng mục | Giá trị | Trạng thái |
|---|---|---|
| Detection window cho Cấp 1 | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-033, BL-009) |
| Detection window cho cover | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-033, BL-009) |
| Detection window cho movement | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-033, BL-009) |
| Mốc bắt đầu tính latency | Chưa có — từ `event_start` hay từ lúc đối tượng vào ROI | `TBD_STAKEHOLDER_APPROVAL` (BC-034, BL-009) |

Không có detection window thì không xác định được TP theo định nghĩa "trong cửa sổ thời gian đã thống nhất" (Mục 3.2 kế hoạch). Đây là blocker chặn toàn bộ KPI.

## 7. ROI

- Việc vẽ, tạo hoặc thay đổi ROI **nằm ngoài phạm vi**; chỉ lưu bằng chứng cấu hình đang áp dụng.
- Bằng chứng bắt buộc cho mỗi event phụ thuộc ROI: `camera_id`, `roi_config_id`/`roi_version`, thời điểm ROI có hiệu lực, snapshot hoặc đường dẫn tham chiếu, vùng ROI liên quan.
- Cách lấy các trường này từ tool: `Open` (BC-036) — owner B.
