# Acceptance Criteria v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Trạng thái:** Active planning specification. Tên `v1.0` là version artifact theo kế hoạch, không phải xác nhận có raw-data result, ground truth hay KPI result.
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 4, 6, 8 và 12.

## 1. Nguyên tắc acceptance

- Đơn vị đánh giá là event; candidate mining không phải ground truth.
- ROI Green/Yellow/Red là review category/evidence; reviewer không gán severity.
- Severity chỉ verify khi alert hệ thống có `rule_engine_rule_id`, version và `rule_engine_severity_output`.
- Ngưỡng KPI kế hoạch theo từng nhóm intrusion, cover và movement: Recall ≥90%, Precision ≥90%, `FP/(TP+FP)` ≤10%.
- `FP/(TP+FP) = 1 − Precision`; không phải false-positive rate `FP/(FP+TN)`.
- Nếu thiếu rule matching, alert output, ground truth reviewed, eligibility hoặc sample hợp lệ: kết luận **Chưa kết luận**.

## 2. Scenario acceptance

| ID | Nhóm | Điều kiện acceptance | Evidence bắt buộc | Trạng thái |
|---|---|---|---|---|
| AC-INT-001 | Intrusion ROI Green | Person liên quan ROI Green được review theo category/evidence; alert category chỉ kiểm tra khi có system access. | Video, source timestamp, ROI reference, alert/log nếu có. | Planned execution. |
| AC-INT-002 | Intrusion ROI Yellow | Person liên quan ROI Yellow được review theo category/evidence; không tách Cấp 2/Cấp 3 bằng nhãn video. | Video, source timestamp, ROI reference, alert/log nếu có. | Planned execution. |
| AC-INT-003 | Intrusion ROI Red | Person liên quan ROI Red/restricted area được review theo category/evidence. | Video, source timestamp, ROI reference, alert/log nếu có. | Planned execution. |
| AC-INT-NEG-001 | Outside ROI | Person ngoài ROI liên quan không bị review như ROI intrusion. | Video, source timestamp, ROI reference. | Planned execution. |
| AC-COV-001 | Cover positive | Positive khi coverage ≥30% **và** duration ≥120 giây. | Video, cover area %, duration, alert/log nếu có. | Rule confirmed; execution pending data. |
| AC-COV-NEG-001 | Cover boundary/interference | Dưới 30% hoặc dưới 120 giây là boundary/negative theo evidence; heavy rain và vehicle glare không bị nhầm là cover. | Video, area %, duration khi cover, timestamp. | Rule confirmed; execution pending data. |
| AC-COV-EDGE-001 | Camera health | Freeze, black screen, video loss không tự gộp vào cover. | Video/log khi có. | System-rule dependency. |
| AC-MOV-001 | Movement positive | Strong shake hoặc camera rotation/changed orientation là positive. | Video/before-after evidence, timestamp, alert/log nếu có. | Rule confirmed; execution pending data. |
| AC-MOV-NEG-001 | Movement interference | Environmental vibration và scene motion không do camera không bị nhầm là movement. Rung nhẹ/không rõ là edge/uncertain. | Video, timestamp. | Rule confirmed; no numeric threshold. |
| AC-DATA-001 | Traceability | Mỗi record có source/camera/sample identity, source-relative timestamps và ROI reference nếu ROI-dependent. | Local manifest/annotation evidence. | Planned execution. |
| AC-DATA-002 | Ground-truth independence | Automation candidate không phải final label; `ambiguous`/`invalid` không vào KPI/golden set. | Review/annotation evidence. | Planned execution. |
| AC-E2E-001 | Alert and rule engine | Khi có system access, đối chiếu camera, timestamp, category và rule-engine severity output tách với review category. | Alert/log, source evidence, rule ID/version. | System-access dependency. |

## 3. Điều kiện loại và kết luận KPI

Loại record khỏi KPI khi source không đọc được, thiếu timestamp/context, thiếu ROI evidence cho case ROI, `ambiguous`/`invalid`/unresolved, hoặc eligibility không đủ cho mục tiêu test.

| Kết luận | Điều kiện |
|---|---|
| Đạt | Đủ evidence/event matching/ground truth/eligibility và mọi KPI nhóm tương ứng đạt target. |
| Không đạt | Đủ điều kiện tính nhưng ít nhất một KPI dưới target. |
| Chưa kết luận | Thiếu data, system rule/output, event-matching rule, ground truth, eligibility hoặc sample hợp lệ. |
| Limitation | Nêu rõ impact và bước tiếp theo; không quy đổi thành Đạt. |

## 4. Dependency execution còn lại

Raw video chỉ nhận từ Week 2. Cần ROI config/version/snapshot/effective time, source/train provenance, alert/log access, event matching/cooldown/dedup rule và latency origin trước khi đánh giá phần phụ thuộc chúng. Không gán owner, approval hoặc deadline chưa có bằng chứng.
