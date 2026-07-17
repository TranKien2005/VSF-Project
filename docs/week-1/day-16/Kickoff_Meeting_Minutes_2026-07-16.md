# Biên bản Kickoff — 16/07/2026

> **Chủ trì:** A — QA Lead / Test Design
> **Thời lượng dự kiến:** 60–90 phút
> **Mục tiêu:** thống nhất phạm vi kiểm thử ba nhóm bài toán, đặt toàn bộ câu hỏi nghiệp vụ và giao owner trả lời trước khi khóa KPI/acceptance criteria ngày 17/07/2026.

> **Trạng thái biên bản:** `Draft — chưa có câu trả lời nghiệp vụ được xác nhận`.
> Tại thời điểm phát hành, chưa có stakeholder nào xác nhận câu trả lời cho các câu hỏi trong [`Business_Clarification_Log_v0.1.md`](./Business_Clarification_Log_v0.1.md). Các mục "Quyết định" bên dưới để trống hoặc `Open` một cách có chủ ý — **không ghi nhận câu trả lời suy diễn**. Biên bản chỉ được chuyển sang `Final` sau khi các bên tham dự xác nhận nội dung và người trả lời được ghi tên cụ thể.

## 1. Thành phần tham dự

| Vai trò | Người | Trách nhiệm trong buổi họp | Trạng thái tham dự |
|---|---|---|---|
| A — QA Lead / Test Design | Thế | Chủ trì, đặt câu hỏi, ghi nhận quyết định | Chủ trì |
| B — Data & Automation | B | Ghi nhận dữ liệu, API, video, ROI evidence | Cần xác nhận |
| C — Annotation & Data Quality | C | Ghi nhận taxonomy và quy tắc gán nhãn | Cần xác nhận |
| AI Team / AI Lead | TBD | Giải thích model đang phát hiện gì, ngưỡng và giới hạn | Cần xác nhận |
| Stakeholder / Product Owner | TBD | Chốt hành vi nào cần cảnh báo, severity, event boundary | Cần xác nhận |
| Vận hành camera / Operations Owner | TBD | Giải thích alert, ROI, log và quy trình xử lý | Cần xác nhận |

> Tên người tham dự và người trả lời phải được điền cụ thể trước khi bất kỳ câu hỏi nào chuyển sang `Answered`.

## 2. Agenda

| Thời gian | Nội dung | Kết quả mong đợi | Trạng thái |
|---:|---|---|---|
| 10 phút | Giới thiệu mục tiêu và phạm vi kiểm thử | Mọi người hiểu phạm vi và giới hạn v1 | Đã trình bày theo [`AI_Testing_Objectives_v0.1.md`](./AI_Testing_Objectives_v0.1.md) |
| 15 phút | Chốt ba nhóm use case: intrusion, cover/tamper, movement | Danh mục use case v0.1 | Đã lập [`Use_Case_Catalogue_v0.1.md`](./Use_Case_Catalogue_v0.1.md) |
| 30 phút | Hỏi câu hỏi nghiệp vụ (object scope, severity, event boundary, cover, movement, KPI, SLA) | Mỗi câu có answer hoặc blocker | 39 câu ghi nhận; 0 câu `Answered` |
| 15 phút | Chốt evidence và KPI đầu vào | Biết cần video/log/ROI reference gì | Evidence tối thiểu đã liệt kê; KPI rule còn `Open` |
| 10 phút | Giao owner và deadline | Không có câu hỏi vô chủ | Mọi câu hỏi đã có owner hỏi và owner phê duyệt |

## 3. Nội dung đã trình bày

### 3.1. Ba phạm vi bắt buộc

1. **Trèo rào/xâm nhập** — lảng vảng ngoài rào, tiếp cận sát rào, chạm/trèo rào, đỉnh rào, vượt rào, vào khu cấm theo ROI.
2. **Che camera/tamper** — che ngắn/dài hạn, một phần/toàn phần, phân biệt với mưa, chói sáng và nhiễu môi trường.
3. **Camera movement** — rung mạnh, xoay/lệch duy trì, phân biệt với rung ngắn do môi trường.

### 3.2. Giới hạn phạm vi đã nêu

- Model AI, firmware và ROI production nằm ngoài phạm vi; không tạo hoặc thay đổi ROI.
- Không stress/load test quy mô lớn, không multi-camera tracking, không pentest, không nhận dạng danh tính.
- Candidate do pipeline mining sinh ra **không phải ground truth**; ground truth do con người review.

### 3.3. KPI đầu vào đã nêu

Recall ≥ 90%, Precision ≥ 90%, `FP/(TP+FP)` ≤ 10% cho từng nhóm, tính riêng. Đã nêu vấn đề M2 và M3 là hai cách nhìn cùng một mẫu số và cần xác nhận tên hiển thị chính thức (`BC-035`).

## 4. Câu hỏi đã đặt và owner

| Nhóm câu hỏi | Số câu | ID | Owner phê duyệt | Hạn chốt |
|---|---:|---|---|---|
| Object scope | 5 | BC-001 … BC-005 | Stakeholder / AI Lead | 16/07/2026 |
| Cấp độ cảnh báo | 5 | BC-006 … BC-010 | Stakeholder | 16/07/2026 |
| Event boundary | 6 | BC-011 … BC-016 | Stakeholder / Operations Owner | 16–17/07/2026 |
| Che camera / tamper | 8 | BC-017 … BC-024 | Stakeholder / AI Lead | 16/07/2026 |
| Camera movement | 5 | BC-025 … BC-029 | AI Lead / Technical Owner | 16/07/2026 |
| KPI và SLA | 6 | BC-030 … BC-035 | Stakeholder / QA Lead / Operations Owner | 17/07/2026 |
| ROI evidence, leakage, ground truth, PII | 4 | BC-036 … BC-039 | Technical Owner / AI Team / Security Owner | 16–17/07/2026 |

## 5. Quyết định

| # | Quyết định | Trạng thái |
|---|---|---|
| D-01 | Phạm vi v1 gồm ba nhóm: intrusion, camera cover/tamper, camera movement | Đề xuất — chờ stakeholder xác nhận |
| D-02 | KPI tính theo event, không theo frame | `Assumption` (`AS-001`) — chờ xác nhận 17/07/2026 |
| D-03 | Candidate mining không được dùng làm ground truth | `Assumption` (`AS-003`) — chờ QA Lead phê duyệt |
| D-04 | Test eligibility là `Unknown` cho tới khi có train manifest từ AI team | `Assumption` (`AS-006`) — chờ AI Team |
| D-05 | Không tạo/thay đổi ROI; chỉ lưu evidence cấu hình đang áp dụng | `Assumption` (`AS-007`) — chờ Technical Owner |
| D-06 | Các câu hỏi chưa có câu trả lời giữ trạng thái `Open`/`Blocked`, không suy diễn | Áp dụng ngay |

> Không có quyết định nghiệp vụ nào được chốt trong buổi kickoff tại thời điểm phát hành biên bản này.

## 6. Blocker nổi bật

| ID | Blocker | Owner xử lý | Ảnh hưởng tới ngày 17 |
|---|---|---|---|
| BL-001 | Chưa có định nghĩa Cấp 2 vs Cấp 3 | Stakeholder | Chặn `Acceptance_Criteria_v1.0` |
| BL-002 | Chưa có cover threshold | AI Lead | Chặn ground truth nhóm cover |
| BL-003 | Chưa có event boundary | Stakeholder | Chặn `Alert_Severity_and_Event_Rule_Spec_v1.0` |
| BL-004 | Chưa có cooldown/dedup | Product Owner | Chặn `Metric_and_KPI_Calculation_Rule_v1.0` |
| BL-006 | Chưa có ngưỡng movement | AI Lead / Technical Owner | Chặn test boundary nhóm movement |

Danh sách đầy đủ: [`Assumption_and_Blocker_Log_v0.1.md`](./Assumption_and_Blocker_Log_v0.1.md).

## 7. Action item

| # | Việc | Owner | Hạn | Status |
|---|---|---|---|---|
| AI-01 | Trả lời nhóm câu hỏi object scope và severity | Stakeholder | 16/07/2026 | Open |
| AI-02 | Trả lời ngưỡng cover (% che, thời lượng) và phân loại freeze/black screen/video loss | AI Lead | 16/07/2026 | Open |
| AI-03 | Trả lời ngưỡng movement (pixel/độ, thời lượng) | AI Lead / Technical Owner | 16/07/2026 | Open |
| AI-04 | Trả lời event boundary và re-entry rule | Stakeholder | 16/07/2026 | Open |
| AI-05 | Trả lời cooldown/dedup, KPI denominator, detection window và latency | Product Owner / Operations Owner | 17/07/2026 | Open |
| AI-06 | Cung cấp cách lấy `roi_config_id`, `roi_version`, snapshot và thời điểm hiệu lực | B ↔ Technical Owner | 16/07/2026 | Open |
| AI-07 | Cung cấp train manifest/source list hoặc xác nhận không có | B ↔ AI Team | 16/07/2026 | Open |
| AI-08 | Review phần data/evidence của use case catalogue và RTM | B | 17/07/2026 | Open |
| AI-09 | Review phần nhãn và event boundary của use case catalogue | C | 17/07/2026 | Open |
| AI-10 | Cập nhật clarification log và chuẩn bị khóa acceptance criteria/KPI rule | A | 17/07/2026 | Open |

## 8. Bước tiếp theo — ngày 17/07/2026

1. Review câu trả lời nhận được; đánh dấu rõ điểm nào chỉ là assumption.
2. Chốt phạm vi MVP và out-of-scope.
3. Khóa quy tắc event-level KPI, mapping alert, duplicate và uncertain/invalid.
4. Chốt owner phê duyệt pass/fail và DoD từng tuần.
5. Với blocker chưa giải quyết: ghi impact và fallback, không tự diễn giải requirement.
