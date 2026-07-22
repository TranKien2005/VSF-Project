# Định nghĩa hành vi gán nhãn

> **Status: human-labeling reference.** Đây là các nhãn do người review xác nhận. Candidate Mining hiện chỉ tạo technical evidence/candidate; không tự kết luận các nhãn trong tài liệu này.

## Nhãn liên quan người

### `xam_nhap_hoac_treo_rao`

Đối tượng tiếp cận khu vực cấm hoặc trèo rào để tiếp cận/đi vào khu vực cấm. Xác định khoảng hành vi chính rồi lấy thêm 30 giây context trước/sau nếu video nguồn còn thời lượng.

### `lang_vang_gan_hang_rao`

Đối tượng vẫn ở ngoài khu vực cấm nhưng đi lại liên tục gần hàng rào. Hành vi phải kéo dài ít nhất 5 phút. Nếu chưa đủ 5 phút thì không dùng nhãn này.

## Nhãn liên quan camera/hình ảnh

### `che_camera_ngan`

Camera che rồi bỏ che ngắt quãng trong cùng chuỗi sự kiện. Chuỗi tính từ lần che đầu đến lần bỏ che cuối phải kéo dài trên 2 phút và mức che lớn hơn 30% khung hình.

### `che_camera_dai`

Camera bị che liên tục hoàn toàn từ 2 phút trở lên và mức che lớn hơn 30% khung hình.

### `camera_rung_lac`

Toàn bộ góc nhìn camera rung lắc tại chỗ. Không dùng nhãn này chỉ vì người, xe hoặc một đối tượng trong cảnh di chuyển.

### `camera_xoay_lech_huong`

Camera xoay sang hướng khác. Không dùng nhãn này cho rung lắc tại chỗ rồi trở về hướng cũ.

### `choi_sang`

Ánh sáng chói làm ảnh hưởng quan sát hình ảnh. Đây là nhãn `positive` độc lập, tương tự các nhãn che camera; không phải condition metadata.

Không có yêu cầu thời lượng tối thiểu/tối đa và không có metadata riêng. Gán nhãn khi người review thấy đủ bằng chứng hình ảnh; lưu start/end sự kiện khi xác định được.

### `nuoc_mua_lam_nhieu_hinh`

Nước mưa, giọt nước hoặc nước vào camera làm nhiễu hình ảnh. Đây là nhãn `positive` độc lập, không phải condition metadata.

Không có yêu cầu thời lượng tối thiểu/tối đa và không có metadata riêng. Gán nhãn khi người review thấy đủ bằng chứng hình ảnh; lưu start/end sự kiện khi xác định được.

## Nhãn bình thường

### `normal`

Không có sự kiện thuộc các nhãn `positive` trong subvideo. `normal` có `label_group = negative`; tất cả nhãn còn lại trong tài liệu này có `label_group = positive`.
