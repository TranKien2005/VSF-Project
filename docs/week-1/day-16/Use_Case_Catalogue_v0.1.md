# Use Case Catalogue v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Trạng thái:** Draft planning catalogue — chưa có raw video, review result hoặc KPI result.
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 4, 6 và 7.

## 1. Quy tắc áp dụng

- Camera reference: HIKVISION `DS-2CD3T46G2-ISU/SL`, firmware `V5.7.55`; khoảng cách camera xấp xỉ 40 m.
- ROI Green/Yellow/Red là bằng chứng category. Reviewer không tự gán Cấp 1–4.
- Severity chỉ là `rule_engine_severity_output` khi hệ thống có output và rule reference.
- Candidate mining POC hiện tại chỉ là person technical evidence, không kết luận intrusion, ROI, cover, movement, severity, ground truth hoặc KPI.

## 2. Intrusion theo ROI

| ID | Scenario | Phân loại review | Evidence tối thiểu | Kết quả cần kiểm tra khi có system access |
|---|---|---|---|---|
| UC-INT-001 | Person liên quan ROI Green | ROI/category evidence | Video, source timestamp, ROI reference | Alert category; rule-engine output nếu có. |
| UC-INT-002 | Person liên quan ROI Yellow | ROI/category evidence | Video, source timestamp, ROI reference | Alert category; rule-engine output nếu có. |
| UC-INT-003 | Person liên quan ROI Red/restricted area | ROI/category evidence | Video, source timestamp, ROI reference | Alert category; rule-engine output nếu có. |
| UC-INT-NEG-001 | Person ngoài ROI liên quan | Hard negative | Video, timestamp, ROI reference | Không nhầm thành ROI intrusion. |
| UC-INT-EDGE-001 | Partial body/ROI boundary hoặc chuyển ROI | Edge/ambiguous | Video, timestamp, ROI reference | Chỉ đánh giá sau khi có event matching/dedup rule. |

Không tạo category/threshold loitering trong catalogue. Mốc 5 phút, nếu có trong system rule, chỉ là context rule engine chứ không phải label/candidate-mining rule.

## 3. Camera cover / tamper

| ID | Scenario | Phân loại review | Evidence tối thiểu | Kết quả cần kiểm tra khi có system access |
|---|---|---|---|---|
| UC-COV-001 | Cover area ≥30% và duration ≥120 giây | Positive | Video, area %, duration, source timestamp | Alert cover category. |
| UC-COV-EDGE-001 | Cover area <30% hoặc duration <120 giây | Boundary/negative | Video, area %, duration | Không tự coi là positive; record evidence. |
| UC-COV-NEG-001 | Heavy rain | Interference/hard negative | Video, timestamp | Không nhầm thành cover. |
| UC-COV-NEG-002 | Vehicle headlight glare | Interference/hard negative | Video, timestamp | Không nhầm thành cover. |
| UC-COV-EDGE-002 | Freeze, black screen, video loss | Camera health/unknown | Video/log khi có | Không tự gộp cover khi không có system rule. |

## 4. Camera movement

| ID | Scenario | Phân loại review | Evidence tối thiểu | Kết quả cần kiểm tra khi có system access |
|---|---|---|---|---|
| UC-MOV-001 | Strong shake | Positive | Video/before-after evidence, timestamp | Alert movement category. |
| UC-MOV-002 | Camera rotation hoặc changed orientation | Positive | Video/before-after evidence, timestamp | Alert movement category. |
| UC-MOV-EDGE-001 | Rung nhẹ/không rõ hoặc temporary shake | Edge/uncertain | Video, timestamp | Không suy diễn numeric threshold. |
| UC-MOV-NEG-001 | Environmental vibration | Negative/interference | Video, timestamp | Không nhầm thành movement. |
| UC-MOV-NEG-002 | Scene motion không do camera | Negative/interference | Video, timestamp | Không nhầm thành movement. |

Không có pixel/degree/duration threshold được đặt trong tài liệu này.

## 5. E2E/data-quality checks

| ID | Kiểm tra | Evidence |
|---|---|---|
| UC-E2E-001 | Alert truy về đúng camera/source timestamp khi có access | Video, alert/log. |
| UC-E2E-002 | ROI-dependent case có ROI config/version/snapshot reference | ROI evidence. |
| UC-E2E-003 | Rule-engine severity, nếu có, được lưu tách với review category | Alert/log và rule ID/version. |
| UC-DATA-001 | Candidate không được dùng làm final ground truth | Human review/annotation record khi có data. |

## 6. Ghi chú execution

Số lượng sample, coverage achieved, alert matching, ground truth và KPI chỉ được tạo/đánh giá từ Week 2–3 khi có dữ liệu thật và evidence tương ứng. Case thiếu context hoặc evidence phải là `ambiguous`/`invalid`, không ép thành positive/negative.
