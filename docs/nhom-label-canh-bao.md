# Danh mục nhãn gán bởi người review

> **Status: human-label vocabulary.** Các nhãn này không phải technical category được Candidate Mining tự sinh.

| Nhóm | Label | Nhãn tổng | Metadata riêng | Yêu cầu thời lượng |
|---|---|---|---|---|
| Người/khu vực cấm | `xam_nhap_hoac_treo_rao` | `positive` | `distance_to_camera`, `lighting_condition` | Không có yêu cầu riêng. |
| Người/hàng rào | `lang_vang_gan_hang_rao` | `positive` | `distance_to_camera`, `lighting_condition` | Tối thiểu 5 phút. |
| Che camera | `che_camera_ngan` | `positive` | Không có | Che/bỏ che ngắt quãng; chuỗi >2 phút và che >30%. |
| Che camera | `che_camera_dai` | `positive` | Không có | Che liên tục hoàn toàn >=2 phút và che >30%. |
| Chuyển động camera | `camera_rung_lac` | `positive` | Không có | Không có yêu cầu riêng. |
| Chuyển động camera | `camera_xoay_lech_huong` | `positive` | Không có | Không có yêu cầu riêng. |
| Chất lượng hình ảnh | `choi_sang` | `positive` | Không có | Không có yêu cầu thời lượng. |
| Chất lượng hình ảnh | `nuoc_mua_lam_nhieu_hinh` | `positive` | Không có | Không có yêu cầu thời lượng. |
| Bình thường | `normal` | `negative` | Không có | Không có sự kiện `positive`. |

`choi_sang` và `nuoc_mua_lam_nhieu_hinh` là nhãn sự kiện độc lập do người review xác nhận. Chúng không phải metadata, không phải hard-negative/interference-only, và không được suy ra tự động từ `camera_anomaly` hoặc technical candidate khác.
