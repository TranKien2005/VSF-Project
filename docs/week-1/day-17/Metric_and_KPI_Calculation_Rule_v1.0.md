# Metric and KPI Calculation Rule v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Reviewer:** B (KPI input table, evidence), C (ground truth status), Stakeholder/QA Lead (phê duyệt)
> **Nguồn requirement:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 3, 8

## 0. Trạng thái phát hành

```text
Status: ASSUMPTION
Approval required from: Mentor/Stakeholder, QA Lead, Operations Owner
Impact: KPI chưa được coi là kết quả chính thức
Fallback: Áp dụng rule tạm thời để dry-run, không khóa golden set
```

## 1. Đơn vị tính

**KPI được tính theo event, không tính theo từng frame.**

- Nguồn: Mục 3.4 kế hoạch — "Tính theo **event**, không tính theo từng frame."
- Trạng thái: `ASSUMPTION` (AS-001, BC-030) — kế hoạch quy định như vậy nhưng stakeholder chưa xác nhận.
- KPI tính **tách riêng** cho ba nhóm: intrusion, cover, movement. Không gộp chung mẫu số.

## 2. Confusion matrix

| Ký hiệu | Định nghĩa |
|---|---|
| TP — Báo đúng | Có ground-truth event và hệ thống báo **đúng loại sự kiện** trong detection window đã thống nhất |
| FP — Báo sai | Hệ thống báo nhưng không có ground-truth event tương ứng, hoặc báo sai loại theo quy tắc mapping đã khóa |
| FN — Không báo | Có ground-truth event nhưng hệ thống không báo trong detection window cho phép |
| TN — Bỏ qua đúng | Không có event và hệ thống không báo |

> TN chỉ đếm được trên các sample negative đã được review và có ranh giới thời gian xác định (ví dụ random background clip). Cách quy đổi TN cho video dài liên tục: `TBD_STAKEHOLDER_APPROVAL`.

## 3. Công thức

```text
Precision          = TP / (TP + FP)
Recall             = TP / (TP + FN)
Tỷ lệ báo động giả = FP / (TP + FP)
```

### 3.1. Cảnh báo về tên gọi M2 — bắt buộc đọc

> `FP/(TP+FP)` **bằng `1 − Precision`**. Đây **không phải** false-positive rate thống kê `FP/(FP+TN)`.

- M2 và M3 là hai cách nhìn trên **cùng một mẫu số** `(TP + FP)`; đạt Precision ≥ 90% thì tự động đạt `FP/(TP+FP)` ≤ 10%. Hai KPI này không độc lập với nhau.
- Báo cáo vẫn hiển thị cả M2 và M3 đúng theo KPI đã giao, nhưng phải kèm ghi chú trên để người đọc không hiểu nhầm là tỷ lệ báo động giả trên tổng số khung hình/thời gian không có event.
- Tên hiển thị chính thức của M2: `TBD_STAKEHOLDER_APPROVAL` (BC-035, Mục 3.3 kế hoạch).
- Nếu stakeholder thực sự cần "tỷ lệ báo động giả" theo nghĩa vận hành (bao nhiêu báo động giả mỗi camera mỗi ngày), phải dùng metric bổ sung ở Mục 8, không dùng M2.

## 4. Matching rule

Một alert được ghép với một ground-truth event khi **thỏa mãn đồng thời**:

1. `camera_id` giống nhau;
2. event type mapping hợp lệ theo bảng mapping đã khóa;
3. thời gian alert nằm trong detection window của event;
4. event đó chưa được ghép với một alert TP khác.

Quy tắc bổ sung:

- Ghép theo thứ tự thời gian: alert **đầu tiên** thỏa mãn cả bốn điều kiện là TP.
- Một alert chỉ được ghép với tối đa một event; một event chỉ sinh tối đa một TP.
- Alert không ghép được với event nào → FP.
- Event không được ghép bởi alert nào → FN.

| Tham số | Giá trị | Trạng thái |
|---|---|---|
| Detection window — intrusion Cấp 1 | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-033) |
| Detection window — cover | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-033) |
| Detection window — movement | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-033) |
| Mốc bắt đầu tính latency | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BC-034) |
| Bảng mapping alert type → event label | Chưa có | `TBD_STAKEHOLDER_APPROVAL` (BL-008) |

> Không có detection window thì **không thể** tính TP/FN. Toàn bộ KPI ở trạng thái **Chưa kết luận** cho tới khi BL-009 được giải quyết.

## 5. Duplicate

- Alert đầu tiên phù hợp với event: **TP**.
- Alert tiếp theo thuộc cùng incident: `duplicate_alert`.
- `duplicate_alert` báo cáo riêng, **không cộng thêm TP** và **không tính FP**.
- Ranh giới "cùng incident" phụ thuộc cooldown và incident merge gap: `TBD_STAKEHOLDER_APPROVAL` (BC-032, BL-004).
- Chuỗi Xanh → Vàng → Đỏ tính là một incident hay nhiều alert: `TBD_STAKEHOLDER_APPROVAL` (BC-013).

Nguồn: Mục 3.4 kế hoạch — "Một ground-truth event và nhiều alert trùng chỉ được tính **một TP**; các alert còn lại được ghi nhận là `duplicate_alert`".

## 6. Misclassification

Tạm thời:

- Alert đúng thời gian nhưng **sai loại sự kiện**: ghi nhận là `misclassification`.
- Cách quy đổi sang FP/FN: `TBD_STAKEHOLDER_APPROVAL` (BC-031, BL-008).

Hai phương án đang chờ stakeholder chọn — **không tự chọn**:

| Phương án | Cách tính | Hệ quả |
|---|---|---|
| P1 | FP cho nhóm bị báo nhầm + FN cho nhóm đúng | Phạt hai lần; Precision và Recall đều giảm |
| P2 | Chỉ ghi `misclassification`, không tính FP/FN | KPI cao hơn; cần metric riêng để không che lỗi |

Nguồn: Mục 3.4 kế hoạch — "Alert sai loại nhưng cùng khoảng thời gian được quy về FP/FN hay `misclassification` phải được thống nhất **trước khi tính KPI**." Vì vậy KPI chính thức không được phát hành trước khi BL-008 đóng.

## 7. Exclusion

Không tính KPI khi:

- `ground_truth_status` là `ambiguous` hoặc `invalid`;
- `needs_second_review` chưa được adjudicate hoặc chưa khóa;
- video hoặc metadata không hợp lệ (thiếu timestamp, file hỏng);
- thiếu ROI reference khi use case phụ thuộc ROI;
- chưa xác định test/train leakage và use case yêu cầu tính độc lập.

Case rerun phải giữ `sample_id`/`run_id`; chỉ kết quả đã được review và khóa mới đưa vào bảng KPI.

## 8. Metric bổ sung

Không thay thế KPI chính thức, dùng để giải thích kết quả:

- false alerts/camera/day hoặc false alerts/camera/hour;
- số critical event (Cấp 1) bị bỏ sót;
- detection/alert latency p50, p95;
- sai số `event_start`/`event_end` giữa ground truth và alert;
- tỷ lệ `duplicate_alert`;
- tỷ lệ candidate mining cần human correction;
- số case `ambiguous`/`invalid` theo nhóm.

## 9. Bảng KPI input tối thiểu

Owner: B. Mỗi dòng là một cặp event–alert hoặc một alert không ghép được:

```text
run_id
event_id
sample_id
source_id
camera_id
roi_version
event_label
event_start_sec
event_end_sec
alert_id
alert_type
alert_timestamp
outcome           # TP | FP | FN | TN | duplicate_alert | misclassification | excluded
exclusion_reason
reviewer
evidence_link
```

## 10. Điều kiện phát hành KPI chính thức

| Điều kiện | Trạng thái |
|---|---|
| Đơn vị tính theo event được stakeholder xác nhận | `ASSUMPTION` — AS-001 |
| Detection window đã chốt cho cả ba nhóm | `Blocked` — BL-009 |
| Quy tắc misclassification đã chốt | `Blocked` — BL-008 |
| Cooldown/dedup đã chốt | `Blocked` — BL-004 |
| Event boundary đã chốt | `Blocked` — BL-003 |
| Ground truth đã khóa và adjudicate | Chưa — Tuần 3 |

> Cả sáu điều kiện đều chưa đạt. **Mọi số liệu KPI tạo ra trước khi các điều kiện trên đóng đều là dry-run và phải ghi rõ `Chưa kết luận`.**
