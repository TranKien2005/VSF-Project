# AI Testing Objectives v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Reviewer:** B (data/evidence), C (label/event boundary), Stakeholder
> **Nguồn requirement:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 2, 3, 4

## 1. Mục tiêu

Xây dựng bộ dữ liệu kiểm thử có thể truy vết và ground truth được con người review cho ba nhóm bài toán AI Camera an ninh vành đai:

1. Trèo rào và xâm nhập.
2. Che camera hoặc camera tamper.
3. Rung lắc, xoay hoặc lệch camera.

> Model AI đã có sẵn và nằm ngoài phạm vi. Repository và kế hoạch này không huấn luyện, thay đổi hoặc đánh giá lại model.

## 2. Mục tiêu kiểm thử

- Đo khả năng phát hiện đúng các event thực tế (Recall).
- Đo số event bị bỏ sót (FN).
- Đo số cảnh báo sai trên video không có event (FP).
- Kiểm tra cảnh báo đúng camera, đúng timestamp, đúng loại sự kiện và đúng cấp độ.
- Kiểm tra alert trùng không kiểm soát (`duplicate_alert`).
- Đảm bảo mỗi sample truy ngược được về video nguồn, `source_id`, camera, ROI reference và reviewer.
- Phân biệt positive với environmental hard negative (mưa, chói đèn, rung ngắn, cây chuyển động).

## 3. KPI dự kiến

Theo Mục 3.1 của kế hoạch, ngưỡng áp dụng cho cả ba nhóm:

| Mã KPI | Nhóm | Chỉ số | Ngưỡng đạt |
|---|---|---|---:|
| M1 | Trèo rào/xâm nhập | Recall | ≥ 90% |
| M2 | Trèo rào/xâm nhập | Tỷ lệ báo động giả `FP/(TP+FP)` | ≤ 10% |
| M3 | Trèo rào/xâm nhập | Precision | ≥ 90% |
| M1 | Che camera | Recall | ≥ 90% |
| M2 | Che camera | Tỷ lệ báo động giả `FP/(TP+FP)` | ≤ 10% |
| M3 | Che camera | Precision | ≥ 90% |
| M1 | Camera movement | Recall | ≥ 90% |
| M2 | Camera movement | Tỷ lệ báo động giả `FP/(TP+FP)` | ≤ 10% |
| M3 | Camera movement | Precision | ≥ 90% |

### 3.1. Công thức

```text
Precision          = TP / (TP + FP)
Recall             = TP / (TP + FN)
Tỷ lệ báo động giả = FP / (TP + FP)
```

### 3.2. Điểm chưa khóa

| Vấn đề | Status | Tham chiếu |
|---|---|---|
| KPI tính theo event (không theo frame) | `Assumption` — cần stakeholder xác nhận 17/07/2026 | `BC-030`, `AS-001` |
| Alert sai loại tính FP+FN hay `misclassification` | `Blocked` | `BC-031` |
| Cooldown/dedup cho nhiều alert trên một event | `Open` | `BC-032`, `BL-004` |
| Detection window và mốc tính latency | `Open` | `BC-033`, `BC-034` |
| Tên hiển thị chính thức của M2 | `Open` — `FP/(TP+FP) = 1 − Precision`, dễ nhầm với `FP/(FP+TN)` | `BC-035` |

`ambiguous` và `invalid` không được dùng để tính KPI chính thức và không đưa vào golden set.

## 4. Trong phạm vi

- Người lảng vảng ngoài hàng rào, tiếp cận sát rào, chạm/bám rào, trèo rào, ở đỉnh rào và vượt rào.
- Người đi vào khu vực cấm theo ROI.
- Che lens một phần hoặc toàn phần, ngắn hạn và dài hạn.
- Rung ngắn, rung môi trường, lệch/xoay camera duy trì và `roi_drift`.
- Positive, negative, hard negative và edge case.
- Evidence: video hoặc proxy clip, alert/log, timestamp, ROI config/version/snapshot reference, reviewer.
- E2E tối thiểu: cảnh báo đúng camera, timestamp, loại/cấp độ và có bằng chứng clip/log.

## 5. Ngoài phạm vi v0.1

Theo Mục 2.3 của kế hoạch:

- Thay đổi, huấn luyện hoặc đánh giá lại model; thay đổi firmware.
- Vẽ, tạo hoặc thay đổi ROI production.
- Kiểm thử an ninh mạng thiết bị, hardening hoặc pentest.
- Multi-camera tracking và nhận dạng cùng đối tượng qua nhiều camera.
- Stress/load test quy mô lớn hoặc nhiều camera đồng thời.
- Fairness chuyên sâu theo nhóm nhân khẩu học; nhận dạng danh tính người.
- Tạo synthetic data ở quy mô lớn.

## 6. Nguyên tắc

- **Candidate do tool sinh ra chỉ là dữ liệu gợi ý để con người review, không phải ground truth** và không được dùng để kết luận KPI/model.
- Clip thiếu context hoặc không thể kết luận phải gán `ambiguous`/`invalid`, không ép thành positive/negative.
- Người tạo artifact không là người duy nhất phê duyệt artifact đó.
- Nếu AI team chưa cung cấp train manifest, test eligibility phải là `Unknown`; không tuyên bố test set độc lập với train data.
- Không commit video, inventory, manifest thực tế, review queue hoặc runtime log vào repository.

## 7. Điều kiện để kết luận KPI

| Trạng thái | Điều kiện |
|---|---|
| **Đạt** | Sample đã khóa/review; Precision ≥ 90%, Recall ≥ 90%, `FP/(TP+FP)` ≤ 10% cho nhóm tương ứng |
| **Không đạt** | Có đủ sample hợp lệ nhưng ít nhất một KPI không đạt |
| **Chưa kết luận** | Sample không đủ, train leakage chưa xác minh, hoặc còn nhiều case unresolved/ambiguous |
| **Rủi ro chấp nhận** | Stakeholder phê duyệt limitation kèm tác động và kế hoạch xử lý |
