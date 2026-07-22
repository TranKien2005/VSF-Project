# Kế hoạch ba tuần kiểm thử AI Camera — tài liệu tham khảo lịch sử

> **Status: historical planning reference.** Kế hoạch này mô tả một chương trình kiểm thử/ground-truth/KPI rộng hơn Candidate Mining hiện tại. Nó không phải contract của ứng dụng đang chạy.

## Phạm vi current implementation

Candidate Mining hiện là local desktop POC chuẩn bị technical evidence:

- import video ngoài repository và lưu metadata/checksum;
- cấu hình một freehand track ROI;
- full-frame person detection với local RT-DETR-L theo cấu hình;
- technical `person_detected` evidence và generic `camera_anomaly` candidate;
- review context và explicit MP4 export.

Ứng dụng hiện không tự tạo ground truth, nhãn xâm nhập/lảng vảng/che camera/rung/xoay cuối cùng, severity, KPI, calibration workflow, hoặc ROI Xanh/Vàng/Đỏ. Những nội dung đó cần một workflow human annotation/rule engine riêng.

## Tài liệu tham chiếu hiện tại

- [README.md](../README.md) — workflow kỹ thuật hiện tại và lệnh chạy.
- [desktop-roi-workflow.md](desktop-roi-workflow.md) — import, ROI, process, review, export hiện tại.
- [huong-dan-gan-nhan.md](huong-dan-gan-nhan.md) — specification nhãn do người review xác nhận.
- [yeu-cau-va-huong-dan-tool-gan-nhan.md](yeu-cau-va-huong-dan-tool-gan-nhan.md) — requirements cho tool gán nhãn riêng.

Nếu triển khai lại kế hoạch ba tuần này, phải đối chiếu từng capability với code/config hiện tại trước khi coi nó là đã có. Raw media, generated evidence, labels, ground truth, manifests và KPI artifacts phải giữ local theo chính sách dữ liệu của repository.
