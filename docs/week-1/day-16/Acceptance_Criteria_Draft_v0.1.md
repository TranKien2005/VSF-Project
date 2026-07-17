# Acceptance Criteria Draft v0.1

> **Ngày:** 16/07/2026  
> **Owner:** A — QA Lead / Test Design  
> **Trạng thái:** Draft planning specification — áp dụng để hoàn thiện acceptance Day 17; không có kết quả thực thi.  
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 4, 6 và 8.

## 1. Nguyên tắc chung

- Đánh giá theo event, không theo frame.
- Candidate của automation chỉ là technical evidence; human review/ground truth quyết định category và boundary.
- ROI Green/Yellow/Red là category/evidence. Reviewer không tự gán severity; severity chỉ verify qua output của rule engine khi có.
- Chưa có raw video trong Week 1. Mọi target dưới đây là specification, không phải KPI/coverage/ground-truth result.

## 2. Điều kiện theo nhóm scenario

| Nhóm | Điều kiện draft | Evidence tối thiểu | Giới hạn |
|---|---|---|---|
| Intrusion | Review event person liên quan ROI Green, Yellow hoặc Red; kiểm tra alert category/timestamp khi có log. | Video nguồn, source timestamp, ROI reference, alert/log nếu có. | Không suy diễn authorization, identity hay Cấp 1–4. |
| Camera cover | Positive khi cover area ≥30% và duration ≥120 giây. Dưới một trong hai ngưỡng là boundary/negative theo evidence. | Video, area %, duration, alert/log nếu có. | Rain và vehicle glare là interference; freeze/black screen/video loss không tự gộp vào cover. |
| Camera movement | Positive khi strong shake hoặc camera rotation/changed orientation. | Video/before-after evidence, source timestamp, alert/log nếu có. | Không có pixel/degree/duration threshold; rung nhẹ/không rõ, environmental vibration và scene motion không do camera là negative/edge. |

## 3. Target KPI và điều kiện kết luận

| Nhóm | Recall target | Precision target | `FP/(TP+FP)` target |
|---|---:|---:|---:|
| Intrusion | ≥ 90% | ≥ 90% | ≤ 10% |
| Camera cover | ≥ 90% | ≥ 90% | ≤ 10% |
| Camera movement | ≥ 90% | ≥ 90% | ≤ 10% |

Chỉ có thể ghi Đạt/Không đạt khi đủ ground truth đã review, event-matching rule, alert evidence, sample eligibility và dữ liệu coverage. Nếu thiếu bất kỳ điều kiện nào, ghi **Chưa kết luận**.

## 4. Phụ thuộc còn lại

Các fact đã có: rule cover 30%/120s; strong shake/rotation là positive movement; rain/glare/scene motion là interference; severity thuộc rule engine.

Các dependency execution còn lại gồm ROI config/version/snapshot/effective time, event matching/cooldown/dedup rule, detection/latency window, train provenance, alert/log access và dữ liệu thật từ Week 2. Các dependency này không được biến thành owner, approval hoặc deadline giả.
