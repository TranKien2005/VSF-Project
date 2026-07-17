# Metric and KPI Calculation Rule v0.1

> **Ngày:** 16/07/2026  
> **Owner:** A — QA Lead / Test Design  
> **Trạng thái:** Draft planning specification — chưa có raw data, ground truth hoặc kết quả KPI.  
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 3, 6, 8 và 9.

## 1. Mục đích và ranh giới

Quy định cách chuẩn bị đánh giá theo **event** cho ba nhóm: intrusion theo ROI, camera cover và camera movement. Tài liệu không đánh giá POC person-detection hiện tại; POC chỉ tạo technical evidence để hỗ trợ review.

Severity/Cấp 1–4 không phải nhãn reviewer và không phải KPI video độc lập. Chỉ đối chiếu `rule_engine_severity_output` khi có alert hệ thống cùng rule ID/version tham chiếu.

## 2. Đơn vị và điều kiện đầu vào

Mỗi event hợp lệ cần có `sample_id`, `source_id`, `camera_id`, source-relative start/end, nhãn review/ground truth, evidence video và alert/log hệ thống khi đánh giá alert. Use case ROI cần ROI config/version/snapshot reference. Case cover ghi `cover_area_percent` và `cover_duration_seconds`.

Không dùng candidate mining output làm ground truth. Không công bố KPI nếu thiếu event-matching rule, dữ liệu alert, ground truth đã review hoặc trạng thái train leakage phù hợp với mục tiêu đánh giá.

## 3. Quy tắc đếm event

| Kết quả | Quy tắc dự kiến |
|---|---|
| TP | Alert đúng nhóm event, khớp event ground truth theo matching rule đã được cung cấp. |
| FP | Alert không khớp event ground truth hợp lệ. |
| FN | Event ground truth hợp lệ không có alert khớp. |
| TN | Chỉ đếm khi protocol có tập negative và định nghĩa window âm rõ ràng. |
| Duplicate alert | Alert bổ sung cho cùng event; báo riêng, không cộng thêm TP. |
| Misclassification | Alert nhầm loại event; cách quy đổi FP/FN phải ghi rõ trong report trước khi kết luận. |

Cooldown, merge/re-entry, detection window, latency origin và cách quy đổi misclassification chưa có rule system cụ thể. Những phần KPI phụ thuộc các rule này có trạng thái **Chưa kết luận**.

## 4. Công thức

```text
Precision          = TP / (TP + FP)
Recall             = TP / (TP + FN)
Tỷ lệ báo động giả = FP / (TP + FP) = 1 − Precision
```

`FP/(TP+FP)` không phải false-positive rate thống kê `FP/(FP+TN)`.

Ngưỡng kế hoạch cho từng nhóm intrusion, cover và movement là Recall ≥ 90%, Precision ≥ 90%, `FP/(TP+FP)` ≤ 10%; đây là target evaluation, không phải kết quả hiện có.

## 5. Exclusion và kết luận

Loại khỏi KPI: `ambiguous`, `invalid`, evidence thiếu context, source không đọc được, thiếu timestamp, thiếu ROI reference cho case ROI, chưa second-review/adjudication, hoặc eligibility không phù hợp.

| Kết luận | Điều kiện |
|---|---|
| Đạt | Đủ sample/event hợp lệ, rule matching, alert evidence và các KPI đạt target. |
| Không đạt | Đủ điều kiện tính nhưng có KPI dưới target. |
| Chưa kết luận | Thiếu input/rule/evidence hoặc sample không đủ. |
| Limitation | Ghi rõ tác động và việc cần làm tiếp; không quy đổi thành Đạt. |
