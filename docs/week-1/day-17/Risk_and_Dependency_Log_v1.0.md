# Risk and Dependency Log v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Nguồn:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 11.3; [`Assumption_and_Blocker_Log_v0.1`](../day-16/Assumption_and_Blocker_Log_v0.1.md)

## 1. Mức độ

| Mức | Ý nghĩa |
|---|---|
| Critical | Chặn KPI hoặc làm sai ground truth; phải xử lý trước khi sang Tuần 2 |
| High | Ảnh hưởng chất lượng dataset hoặc độ tin cậy kết luận |
| Medium | Ảnh hưởng tiến độ hoặc phạm vi, có phương án thay thế |

## 2. Risk và dependency

| ID | Rủi ro/Dependency | Impact | Mức độ | Owner | Mitigation/Fallback | Deadline | Status | Blocker liên quan |
|---|---|---|---|---|---|---|---|---|
| R-001 | Chưa chốt event boundary (start/end, một phần cơ thể vào ROI, trèo rồi quay xuống) | Sai TP/FN; nhãn boundary không nhất quán giữa reviewer | Critical | A/C | Không khóa KPI; dùng assumption có phê duyệt; bất đồng đưa `needs_second_review` | 17/07/2026 — quá hạn | Open | BL-003 |
| R-002 | Chưa chốt cooldown/dedup và incident merge gap | TP bị đếm lặp; không tính được duplicate | Critical | A | Báo `duplicate_alert` riêng, không cộng vào TP | 17/07/2026 — quá hạn | Open | BL-004 |
| R-003 | Không có train manifest từ AI team | Có nguy cơ leakage; không chứng nhận test độc lập | High | B | Gắn trạng thái `Unknown`, ghi limitation trong dataset card | Tuần 2 | Open | AS-006 |
| R-004 | Thiếu ROI version/snapshot reference | Không truy vết được alert theo ROI; test nhầm giữa các phiên bản ROI | High | B | Loại sample khỏi KPI phụ thuộc ROI | Trước annotation | Open | BC-036 |
| R-005 | Thiếu negative và hard negative sample | Tỷ lệ báo động giả không đáng tin | High | A/B | Tăng quota random background và risk-based sample | Tuần 2 | Open | — |
| R-006 | Nhãn của A/B/C không thống nhất | Ground truth sai | High | C | Calibration 30–50 clip, blind review và adjudication | Tuần 2 | Open | — |
| R-007 | Thiếu quyền truy cập video/camera/log/API | Không dry-run E2E được; không có evidence alert | Critical | B | Escalate mentor/stakeholder ngay | Ngay | Open | — |
| R-008 | Chưa chốt cover threshold (% che và thời lượng) | Positive/negative nhóm cover bị lẫn | Critical | A/AI Lead | Không khóa ground truth nhóm cover; chỉ ghi nhận quan sát | 17/07/2026 — quá hạn | Open | BL-002 |
| R-009 | Chưa chốt ngưỡng movement (pixel/độ, thời lượng) | Không phân biệt `temporary_shake` và `sustained_camera_displacement` | Critical | A/AI Lead | Ghi before/after frame, không khóa nhãn movement | 17/07/2026 — quá hạn | Open | BL-006 |
| R-010 | Chưa chốt Cấp 2 vs Cấp 3 | Severity không nhất quán | Critical | A/Stakeholder | `needs_second_review`; không khóa severity | 17/07/2026 — quá hạn | Open | BL-001 |
| R-011 | Chưa chốt detection window và mốc latency | Không xác định được TP; không đánh giá E2E | Critical | A/Product Owner | Ghi latency thô, kết luận `Chưa kết luận` | 17/07/2026 — quá hạn | Open | BL-009 |
| R-012 | Chưa chốt alert sai loại là FP+FN hay misclassification | KPI không nhất quán giữa ba nhóm | Critical | A/Stakeholder | Báo cáo cả hai cách tính kèm ghi chú | 17/07/2026 — quá hạn | Open | BL-008 |
| R-013 | Chưa chốt object scope và whitelist | Không xác định TP/FP cho negative có người/xe/động vật | High | A/Stakeholder | Gán `ambiguous` cho case ngoài phạm vi người | 17/07/2026 — quá hạn | Open | BL-007 |
| R-014 | Chưa chốt freeze/black screen/video loss là tamper hay camera health | Sai mẫu số KPI nhóm cover | High | A/AI Lead | Gán nhãn camera health riêng, tách khỏi KPI cover | 17/07/2026 — quá hạn | Open | BL-005 |
| R-015 | Video quá lớn hoặc máy hạn chế tài nguyên | Chậm mining và review | Medium | B | Streaming, sampling, proxy clip, một worker/model nhỏ | Tuần 2 | Open | — |
| R-016 | Mining bỏ sót event | Dataset thiên lệch; recall của mining không đo được | High | B/C | Random background 20% và risk-based 10% | Tuần 2 | Open | — |
| R-017 | Reviewer bị output của model ảnh hưởng (automation bias) | Ground truth mất tính độc lập | High | C | Blind review, golden review độc lập | Tuần 2 | Open | AS-003 |
| R-018 | Nhiều clip trùng hoặc gần trùng | KPI sai lệch | High | B | Source-group split, checksum/fingerprint | Tuần 2 | Open | — |
| R-019 | Không đủ positive event trong dữ liệu thực | Coverage thấp; KPI mẫu nhỏ | High | A | Controlled scenario; synthetic data ở phase sau | Tuần 2 | Open | — |
| R-020 | Video chứa PII (mặt người, biển số) | Rủi ro bảo mật và tuân thủ | High | B/C | Access control, retention/masking theo policy; không commit vào repo | Tuần 2 | Open | BC-039 |
| R-021 | KPI tính trên mẫu nhỏ | Kết luận không tin cậy | High | A | Ghi `Chưa kết luận`, nêu sample size và limitation | Tuần 3 | Open | — |

## 3. Dependency bên ngoài

| ID | Dependency | Người cung cấp | Cần trước | Trạng thái |
|---|---|---|---|---|
| D-001 | Câu trả lời nghiệp vụ cho BC-001 … BC-035 | Stakeholder, AI Lead, Operations Owner | Khóa acceptance criteria và KPI | Chưa có |
| D-002 | Train manifest/checksum/source list | AI Team | Xác định test eligibility | Chưa có |
| D-003 | Cách lấy `roi_config_id`, `roi_version`, snapshot | Technical Owner (qua B) | Annotation và KPI phụ thuộc ROI | Chưa có |
| D-004 | Quyền truy cập raw video, camera, log/API, storage | Security/Data Owner (qua B) | Dry-run E2E | Chưa có |
| D-005 | Chính sách PII, retention và quyền truy cập | Security/Data Owner | Lưu trữ và bàn giao dataset | Chưa có |
| D-006 | Nguồn ground truth chuẩn và người adjudicate | Stakeholder (qua C) | Khóa nhãn cuối | Chưa có |

## 4. Đánh giá gate Tuần 1

| Điều kiện gate (Mục 7 kế hoạch) | Trạng thái |
|---|---|
| Có owner phê duyệt scope/pass-fail hoặc assumption đã được chấp nhận | **Chưa đạt** — chưa có phê duyệt |
| Cấp 2/Cấp 3, Cấp 1 boundary, cover/tamper và movement boundary đủ để gán nhãn | **Chưa đạt** — R-001, R-008, R-009, R-010 |
| KPI chốt theo event và cách đếm TP/FP/FN rõ ràng | **Chưa đạt** — R-011, R-012 |
| Biết data source, quyền truy cập, metadata tối thiểu và cách tham chiếu ROI version | **Chưa đạt** — R-004, R-007 (owner B) |
| Chọn được tool/phương án review | Owner C — chưa xác nhận |
| Dry run tạo được evidence đủ cho ít nhất một case mỗi nhóm | Owner B — chưa xác nhận |

> **Kết luận:** gate Tuần 1 **chưa đủ điều kiện mở**. Rủi ro chính là 7 blocker Critical đã quá hạn 17/07/2026. Cần escalate tới mentor/stakeholder trước khi bắt đầu Tuần 2, hoặc chấp nhận chuyển Tuần 2 với phạm vi giới hạn: chỉ inventory và mining, không khóa ground truth và không tính KPI.
