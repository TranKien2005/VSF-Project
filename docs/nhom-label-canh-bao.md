# Danh mục nhãn

| Nhóm | Label | Ý nghĩa | Loại dữ liệu | Khoảng cách |
|---|---|---|---|---|
| Đột nhập/Trèo rào | `nguoi_lang_vang` | Người di chuyển hoặc đứng lâu trong ROI xanh | `positive` | tối đa là 40 m |
| Đột nhập/Trèo rào | `nguoi_tiep_can_hang_rao` | Người đi vào hoặc chạm ROI vàng sát hàng rào | `positive` | tối đa là 40 m |
| Đột nhập/Trèo rào | `nguoi_treo_rao` | Người trèo lên hàng rào, chạm ROI đỏ hoặc vào khu cấm | `positive` | tối đa là 40 m|
| Che camera | `che_camera_ngan` | Camera bị che nhưng thời gian dưới 2 phút | `positive` | — |
| Che camera | `che_camera_dai` | Camera bị che liên tục từ 2 phút trở lên và diện tích che đạt ngưỡng | `positive` | — |
| Che camera | `choi_den_xe` | Ánh đèn xe quét qua camera gây sáng hoặc tối hình tạm thời | `positive` | — |
| Che camera | `mua_lam_nhieu_hinh` | Mưa lớn, giọt nước hoặc sương làm nhiễu hình ảnh | `positive` | — |
| Xoay/rung camera | `lac_camera_manh` | Camera rung mạnh làm thay đổi hình ảnh hoặc góc nhìn rõ rệt | `positive` | — |
| Xoay/rung camera | `xoay_lech_camera` | Camera bị xoay và giữ ở hướng khác so với hướng chuẩn | `positive` | — |
| Xoay/rung camera | `rung_nhe_tam_thoi` | Camera rung nhẹ do gió, phương tiện hoặc tác động nhỏ rồi trở lại bình thường | `positive` | — |
| Chung | `binh_thuong` | Video hoạt động bình thường, không có sự kiện bất thường | `positive` | — |
