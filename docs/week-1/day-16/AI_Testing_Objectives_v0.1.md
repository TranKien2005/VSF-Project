# AI Testing Objectives v0.1

> **Ngày:** 16/07/2026
> **Owner:** A — QA Lead / Test Design
> **Reviewer:** B (data/evidence), C (label/event boundary)
> **Trạng thái:** Draft planning specification — chưa có raw data, annotation, ground truth hoặc KPI result.
> **Nguồn requirement:** [`docs/ke-hoach-3-tuan-kiem-thu-ai-camera.md`](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md) — Mục 4, 6, 7 và 8
> **Fact mentor đã áp dụng:** HIKVISION DS-2CD3T46G2-ISU/SL, firmware V5.7.55, khoảng cách camera xấp xỉ 40 m; ROI Green/Yellow/Red; cover ≥30% trong ≥120 giây; movement positive là strong shake hoặc rotation/changed orientation; severity do rule engine quyết định.

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
- Kiểm tra cảnh báo đúng camera, timestamp và loại sự kiện; chỉ đối chiếu severity với `rule_engine_severity_output` khi hệ thống cung cấp output cùng rule reference.
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

### 3.2. Điều kiện execution chưa có system/data evidence

| Nội dung | Trạng thái áp dụng |
|---|---|
| KPI tính theo event (không theo frame) | Quy tắc kế hoạch; chỉ report chính thức sau khi có event matching, alert evidence và ground truth hợp lệ. |
| Alert sai loại | Report riêng là `misclassification`; cách quy đổi FP/FN phải ghi rõ trước khi kết luận. |
| Cooldown/dedup | Chưa có incident rule cụ thể; duplicate được report riêng, phần KPI phụ thuộc rule là `Chưa kết luận`. |
| Detection window/latency | Chưa có system time origin/window; không đặt target hoặc kết quả latency giả. |
| M2 | `FP/(TP+FP) = 1 − Precision`, không phải false-positive rate `FP/(FP+TN)`. |

`ambiguous` và `invalid` không được dùng để tính KPI chính thức và không đưa vào golden set.

## 4. Trong phạm vi

- Person liên quan ROI Green, Yellow hoặc Red; authorization/identity không được suy diễn.
- Camera cover positive khi ≥30% diện tích cover trong ≥120 giây; rain và vehicle glare là interference.
- Camera movement positive khi strong shake hoặc rotation/changed orientation; scene motion không do camera là interference.
- Positive, negative, hard negative, edge và ambiguous case.
- Evidence: raw video/source timestamp, ROI config/version/snapshot reference, alert/log khi có và reviewer; manual export clip chỉ là evidence phụ.
- E2E tối thiểu: alert đúng camera, timestamp, loại; severity chỉ đối chiếu qua output rule engine khi có.

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
- Nếu không có train manifest/source list, test eligibility phải là `Unknown`; không tuyên bố test set độc lập với train data.
- Không commit video, inventory, manifest thực tế, review queue hoặc runtime log vào repository.

## 7. Điều kiện để kết luận KPI

| Trạng thái | Điều kiện |
|---|---|
| **Đạt** | Sample đã khóa/review; Precision ≥ 90%, Recall ≥ 90%, `FP/(TP+FP)` ≤ 10% cho nhóm tương ứng |
| **Không đạt** | Có đủ sample hợp lệ nhưng ít nhất một KPI không đạt |
| **Chưa kết luận** | Sample không đủ, train leakage chưa xác minh, hoặc còn nhiều case unresolved/ambiguous |
| **Rủi ro chấp nhận** | Limitation có tác động và kế hoạch xử lý được ghi rõ; không quy đổi thành kết luận KPI Đạt. |
