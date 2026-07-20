# Danh mục nhãn và kết quả cảnh báo

| Nhóm | Label | Ý nghĩa | Loại dữ liệu | Kết quả cảnh báo |
|---|---|---|---|---|
| Đột nhập/Trèo rào | `nguoi_lang_vang` | Người di chuyển hoặc đứng lâu trong ROI xanh | `positive` | Cấp 4 khi đủ thời gian quy định |
| Đột nhập/Trèo rào | `nguoi_tiep_can_hang_rao` | Người đi vào hoặc chạm ROI vàng sát hàng rào | `positive` | Cấp 2–3 |
| Đột nhập/Trèo rào | `nguoi_treo_rao` | Người trèo lên hàng rào, chạm ROI đỏ hoặc vào khu cấm | `positive` | Cấp 1 |
| Che camera | `che_camera_ngan` | Camera bị che nhưng thời gian dưới 2 phút | `positive / edge_case` | Không cảnh báo nếu chưa đủ 2 phút |
| Che camera | `che_camera_dai` | Camera bị che liên tục từ 2 phút trở lên và diện tích che đạt ngưỡng | `positive` | Cấp 1 |
| Che camera | `choi_den_xe` | Ánh đèn xe quét qua camera gây sáng hoặc tối hình tạm thời | `hard_negative` | Không cảnh báo |
| Che camera | `mua_lam_nhieu_hinh` | Mưa lớn, giọt nước hoặc sương làm nhiễu hình ảnh | `hard_negative` | Không cảnh báo |
| Xoay/rung camera | `lac_camera_manh` | Camera rung mạnh làm thay đổi hình ảnh hoặc góc nhìn rõ rệt | `positive` | Cấp 1 |
| Xoay/rung camera | `xoay_lech_camera` | Camera bị xoay và giữ ở hướng khác so với hướng chuẩn | `positive` | Cấp 1 |
| Xoay/rung camera | `rung_nhe_tam_thoi` | Camera rung nhẹ do gió, phương tiện hoặc tác động nhỏ rồi trở lại bình thường | `hard_negative` | Không cảnh báo |
| Chung | `binh_thuong` | Video hoạt động bình thường, không có sự kiện bất thường | `negative` | Không cảnh báo |
