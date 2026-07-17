# Use Case Catalogue v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Reviewer:** B (evidence khả thi), C (nhãn và event boundary)
> **Nguồn taxonomy:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 4

Cột "Kết quả mong đợi" chỉ được coi là khóa khi các câu hỏi tương ứng trong [`Business_Clarification_Log_v0.1.md`](./Business_Clarification_Log_v0.1.md) chuyển sang `Answered`. Các mục ghi `TBD` là chưa có rule nghiệp vụ.

## 1. Intrusion — trèo rào/xâm nhập

| ID | Use case | Nhãn taxonomy | Loại | Kết quả mong đợi | Evidence | Clarification |
|---|---|---|---|---|---|---|
| UC-INT-001 | Người lảng vảng ngoài hàng rào (ROI Xanh) | `person_near_fence` | Edge/positive tùy rule | Cảnh báo Cấp 4 theo dõi, hoặc không alert — TBD | Video (cửa sổ 5 phút), ROI reference, alert log | BC-006, BC-008 |
| UC-INT-002 | Người tiếp cận sát hàng rào (ROI Vàng) | `person_approaching_fence` | Positive | Alert Cấp 2 hoặc 3 — TBD rule phân biệt | Video, ROI reference, alert log | BC-007, BC-008 |
| UC-INT-003 | Người chạm hoặc bám hàng rào | `person_touching_fence` | Positive | Alert đúng loại; cấp theo ROI Vàng/Đỏ thực tế — TBD | Video, ROI reference, alert log | BC-006 |
| UC-INT-004 | Người trèo lên hàng rào | `person_climbing_fence` | Positive | Alert intrusion; cấp theo event boundary — TBD | Video, timestamp, alert log | BC-009, BC-011 |
| UC-INT-005 | Người ở đỉnh hàng rào | `person_on_fence_top` | Positive | Ứng viên Cấp 1 — TBD | Video, ROI reference, alert log | BC-009 |
| UC-INT-006 | Người vượt qua hàng rào vào ROI Đỏ | `person_crossing_fence` | Critical positive | Alert Cấp 1 khẩn cấp | Video, ROI Đỏ reference, alert log, timestamp | BC-005, BC-016 |
| UC-INT-007 | Người ở trong khu vực cấm | `person_inside_restricted_area` | Critical positive | Alert Cấp 1 khẩn cấp | Video, ROI reference, alert log | BC-010 |
| UC-INT-NEG-001 | Có người nhưng hoàn toàn ngoài ROI | `person_outside_roi` | Hard negative | Không alert intrusion | Video, ROI reference | BC-004 |
| UC-INT-NEG-002 | Động vật đi qua vùng ROI | — | Negative/TBD | Không alert nếu ngoài object scope | Video, ROI reference | BC-001 |
| UC-INT-NEG-003 | Xe đi qua vùng ROI | — | Negative/TBD | Không alert nếu ngoài object scope | Video, ROI reference | BC-001 |
| UC-INT-NEG-004 | Nhân viên nội bộ/bảo vệ tuần tra trong ROI | — | Hard negative/TBD | Theo whitelist rule — TBD | Video, ROI reference, lịch tuần tra | BC-002, BC-003 |
| UC-INT-EDGE-001 | Người trèo lên rồi quay xuống phía ngoài | `person_climbing_fence` | Edge | TBD stakeholder — có tính Cấp 1 không | Video, event boundary, alert log | BC-009 |
| UC-INT-EDGE-002 | Chỉ một phần cơ thể (tay/chân) vào ROI Đỏ | — | Edge | TBD stakeholder | Video, ROI Đỏ reference | BC-005, BC-016 |
| UC-INT-EDGE-003 | Một người di chuyển Xanh → Vàng → Đỏ liên tục | — | Edge/dedup | TBD — một incident hay nhiều alert | Video, alert log, timestamp | BC-013, BC-032 |
| UC-INT-EDGE-004 | Hai người xuất hiện đồng thời trong ROI | — | Edge/dedup | TBD — một hay hai event | Video, alert log | BC-014 |
| UC-INT-EDGE-005 | Người rời ROI rồi quay lại sau thời gian ngắn | — | Edge/dedup | TBD — re-entry rule và cooldown | Video, alert log, timestamp | BC-015, BC-032 |

## 2. Camera cover / tamper

| ID | Use case | Nhãn taxonomy | Loại | Kết quả mong đợi | Evidence | Clarification |
|---|---|---|---|---|---|---|
| UC-COV-001 | Che gần/toàn bộ lens đủ thời lượng | `lens_full_cover` | Positive | Alert camera cover | Video, alert log, timestamp | BC-018 |
| UC-COV-002 | Che một phần lens | `lens_partial_cover` | Edge/positive | Theo ngưỡng % che đã chốt — TBD | Video, alert log | BC-017, BC-019 |
| UC-COV-003 | Che lens trong thời gian rất ngắn | `temporary_occlusion` | Edge | Theo duration rule — TBD | Video, alert log | BC-018, BC-020 |
| UC-COV-NEG-001 | Ánh đèn xe chiếu trực tiếp vào camera | `headlight_glare` | Hard negative | Không nhầm thành cover | Video, alert log | BC-023 |
| UC-COV-NEG-002 | Mưa lớn | `rain_heavy` | Hard negative/TBD | Theo rule nghiệp vụ — tamper hay camera health | Video, alert log | BC-021 |
| UC-COV-NEG-003 | Sương mờ hoặc giọt nước trên lens | `water_drop_or_fog` | Hard negative/TBD | Theo rule nghiệp vụ | Video, alert log | BC-022 |
| UC-COV-NEG-004 | Điều kiện thiếu sáng ban đêm | `low_light` | Hard negative/quality condition | Không nhầm thành cover | Video, alert log | BC-021 |
| UC-COV-NEG-005 | Vật thể đi ngang lens trong 1–2 giây | `temporary_occlusion` | Hard negative/TBD | Theo duration rule | Video | BC-018, BC-020 |
| UC-COV-EDGE-001 | Video freeze | `video_freeze` | Camera health/TBD | Không tự gộp vào cover khi chưa có rule | Log, video | BC-024 |
| UC-COV-EDGE-002 | Black screen | `black_screen` | Camera health/TBD | TBD — tamper hay camera health | Log, video | BC-024 |
| UC-COV-EDGE-003 | Video loss / mất hình | `video_loss` | Camera health/TBD | TBD — tamper hay camera health | Log | BC-024 |

## 3. Camera movement — rung lắc/xoay lệch

| ID | Use case | Nhãn taxonomy | Loại | Kết quả mong đợi | Evidence | Clarification |
|---|---|---|---|---|---|---|
| UC-MOV-001 | Camera bị xoay lệch hướng và giữ nguyên vị trí mới | `sustained_camera_displacement` | Positive | Alert movement | Before/after frame, alert log, timestamp | BC-025, BC-026 |
| UC-MOV-002 | Camera lệch làm ROI không còn bám đúng vùng vật lý | `roi_drift` | Positive | Alert movement hoặc camera-health event — TBD | ROI snapshot before/after, video, log | BC-028 |
| UC-MOV-003 | Rung mạnh kéo dài | `sustained_camera_displacement` | Positive | Alert movement theo duration rule — TBD | Video, alert log | BC-026 |
| UC-MOV-NEG-001 | Camera rung ngắn rồi trở lại vị trí cũ | `temporary_shake` | Hard negative/edge | Theo duration rule — TBD | Video, alert log | BC-026, BC-027 |
| UC-MOV-NEG-002 | Rung do gió, xe hoặc cổng đóng mở | `environmental_vibration` | Hard negative | Không alert movement | Video, alert log | BC-027, BC-029 |
| UC-MOV-NEG-003 | Cây hoặc vật thể lớn trong cảnh chuyển động | `scene_change_non_camera_move` | Hard negative | Không alert movement | Video | BC-029 |
| UC-MOV-NEG-004 | Ánh sáng thay đổi làm toàn cảnh đổi (đèn bật/tắt, bình minh) | `scene_change_non_camera_move` | Hard negative | Không alert movement | Video | BC-029 |

## 4. E2E tối thiểu

| ID | Use case | Loại | Kết quả mong đợi | Evidence | Clarification |
|---|---|---|---|---|---|
| UC-E2E-001 | Alert gắn đúng `camera_id` và timestamp của event | E2E | Alert khớp camera và thời điểm trong cửa sổ cho phép | Video, timestamp, alert log | BC-033, BC-034 |
| UC-E2E-002 | Alert có đúng loại sự kiện và cấp độ | E2E | Loại/severity khớp ground truth | Alert log, ground truth | BC-006, BC-031 |
| UC-E2E-003 | Alert có bằng chứng clip/log truy vết được | E2E | Có clip hoặc log liên kết `sample_id`/`source_id` | Clip, log, manifest reference | — |
| UC-E2E-004 | Không có alert trùng không kiểm soát cho một event | E2E/dedup | Một TP; alert còn lại ghi `duplicate_alert` | Alert log, timestamp | BC-032 |
| UC-E2E-005 | Alert truy ngược được về ROI config/version đang áp dụng | E2E | Có `roi_config_id`/`roi_version` và thời điểm hiệu lực | ROI snapshot reference | BC-036 |

## 5. Ghi chú

- Toàn bộ use case cần evidence tối thiểu theo Mục 9.2 của kế hoạch: sample/source/camera ID; video hoặc proxy clip và timestamp; ROI config/version/snapshot reference; ground truth và reviewer; alert/log; expected/actual/verdict; `run_id` và link evidence.
- Việc vẽ hoặc thay đổi ROI nằm ngoài phạm vi; chỉ lưu bằng chứng cấu hình ROI đang áp dụng.
- Số lượng sample cho mỗi use case chưa được quyết định ở v0.1; quota coverage thuộc `Sampling_Strategy` (Tuần 2).
