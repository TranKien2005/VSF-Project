# Hướng dẫn gán nhãn subvideo Camera AI

> **Status: specification for a separate human-labeling workflow.** The current Candidate Mining application produces technical evidence only; it does not currently persist the final labels or metadata defined here.

## 1. Đơn vị dữ liệu

Mỗi đơn vị dữ liệu là một **subvideo** và chỉ có **một nhãn sự kiện duy nhất**.

Một video nguồn có thể có nhiều sự kiện. Khi đó tách thành nhiều subvideo; không gộp nhiều loại sự kiện vào một subvideo.

Mỗi đơn vị dữ liệu phải lưu:

```text
camera_name
video_name
label
label_group
subvideo_start_time
subvideo_end_time
```

Để hệ thống tạo subvideo cho các nhãn có hành vi chính (`xam_nhap_hoac_treo_rao` và `lang_vang_gan_hang_rao`), người gán nhãn cần xác định thêm vùng thời gian hành vi chính:

```text
event_start_time
event_end_time
```

- Các mốc thời gian tính bằng giây, theo thời gian của video nguồn.
- `subvideo_start_time` và `subvideo_end_time` là thời điểm bắt đầu/kết thúc của đoạn subvideo được lấy ra.
- `event_start_time` và `event_end_time` là thời điểm bắt đầu/kết thúc của hành vi chính để hệ thống tạo subvideo đúng ngữ cảnh.

## 2. Danh mục nhãn

| Nhãn | Nhãn tổng | Ý nghĩa |
|---|---|---|
| `xam_nhap_hoac_treo_rao` | `positive` | Đối tượng tiếp cận khu vực cấm hoặc trèo rào để tiếp cận/đi vào khu vực cấm. |
| `lang_vang_gan_hang_rao` | `positive` | Đối tượng ở bên ngoài khu vực cấm và đi lại liên tục gần hàng rào khoảng 5 phút. |
| `che_camera_ngan` | `positive` | Camera bị che ngắt quãng: che rồi bỏ ra lặp lại trong một chuỗi sự kiện kéo dài trên 2 phút. |
| `che_camera_dai` | `positive` | Camera bị che liên tục hoàn toàn từ 2 phút trở lên. |
| `camera_rung_lac` | `positive` | Camera rung lắc tại chỗ. |
| `camera_xoay_lech_huong` | `positive` | Camera xoay sang hướng khác. |
| `choi_sang` | `positive` | Ánh sáng chói làm ảnh hưởng quan sát hình ảnh. |
| `nuoc_mua_lam_nhieu_hinh` | `positive` | Nước mưa, giọt nước hoặc nước vào camera làm nhiễu hình ảnh. |
| `normal` | `negative` | Không có sự kiện thuộc các nhãn `positive`. |

Tám nhãn sự kiện đầu tiên đều có `label_group = "positive"`. Chỉ nhãn `normal` có `label_group = "negative"`.

## 3. Mô tả từng nhãn và metadata áp dụng

### 3.1. `xam_nhap_hoac_treo_rao`

**Định nghĩa:** đối tượng tiếp cận khu vực cấm hoặc trèo rào để tiếp cận/đi vào khu vực cấm.

**Cách xác định thời gian:**

1. Xác định `event_start_time` tại thời điểm bắt đầu hành vi tiếp cận khu vực cấm hoặc trèo rào.
2. Xác định `event_end_time` tại thời điểm hành vi kết thúc.
3. Hệ thống tự tạo subvideo bằng cách thêm 30 giây trước và 30 giây sau vùng hành vi chính:

```text
subvideo_start_time = max(0, event_start_time - 30 giây)
subvideo_end_time   = min(thời_lượng_video_nguồn, event_end_time + 30 giây)
```

**Metadata áp dụng:** ngoài metadata chung, lưu bốn trường sau:

```text
distance_to_camera
lighting_condition
```

| Trường | Giá trị được lưu | Lưu ý |
|---|---|---|
| `distance_to_camera` | `5m`, `10m`, `15m`, `20m`, `25m`, `30m`, `35m`, `40m` | Khoảng cách từ đối tượng đến camera. |
| `lighting_condition` | `ngay`, `dem_co_den`, `dem_khong_den` | Điều kiện ánh sáng của sự kiện. |

### 3.2. `lang_vang_gan_hang_rao`

**Định nghĩa:** đối tượng chưa vào khu vực cấm, vẫn ở bên ngoài và đi lại liên tục gần hàng rào trong khoảng 5 phút.

**Cách xác định thời gian:**

1. Xác định `event_start_time` từ khi đối tượng bắt đầu đi lại/lưu lại gần hàng rào ở bên ngoài khu vực cấm.
2. Xác định `event_end_time` khi hành vi lảng vảng kết thúc.
3. Khoảng thời gian hành vi phải đủ ít nhất 5 phút:

```text
event_end_time - event_start_time >= 300 giây
```

4. Nếu đoạn ban đầu ngắn hơn 5 phút, phải kéo subvideo để có đủ 5 phút bằng chứng lảng vảng.
5. Sau khi xác định đủ vùng hành vi, hệ thống tự thêm 30 giây đầu/cuối nếu video nguồn còn thời lượng.

Không dùng nhãn này khi đối tượng đã tiếp cận khu vực cấm; trường hợp đó dùng `xam_nhap_hoac_treo_rao`.

**Metadata áp dụng:** giống `xam_nhap_hoac_treo_rao`:

```text
distance_to_camera
lighting_condition
```

| Trường | Giá trị được lưu | Lưu ý |
|---|---|---|
| `distance_to_camera` | `5m`, `10m`, `15m`, `20m`, `25m`, `30m`, `35m`, `40m` | Khoảng cách từ đối tượng đến camera. |
| `lighting_condition` | `ngay`, `dem_co_den`, `dem_khong_den` | Điều kiện ánh sáng của sự kiện. |

### 3.3. `che_camera_ngan`

**Định nghĩa:** camera bị che **ngắt quãng**: có các lần che rồi bỏ che, lặp lại trong cùng một chuỗi sự kiện.

**Điều kiện gán nhãn:**

1. Chuỗi che/bỏ che kéo dài **trên 2 phút**. Thời gian được tính từ lần che đầu tiên đến lần bỏ che cuối cùng của chuỗi, bao gồm cả các khoảng bỏ che ở giữa.
2. Mức che của sự kiện lớn hơn **30% khung hình**.
3. Không yêu cầu camera bị che liên tục toàn bộ thời gian; đặc điểm của nhãn này là che rồi bỏ ra, lặp lại.

**Cách xác định thời gian và subvideo:**

- `event_start_time`: thời điểm bắt đầu lần che đầu tiên trong chuỗi.
- `event_end_time`: thời điểm kết thúc lần bỏ che cuối cùng trong chuỗi.
- Hệ thống tạo subvideo với 30 giây trước và 30 giây sau khoảng sự kiện, nếu video nguồn còn thời lượng.

**Metadata áp dụng:** chỉ metadata chung. Không lưu `distance_to_camera` hoặc `lighting_condition` cho nhãn này.

### 3.4. `che_camera_dai`

**Định nghĩa:** camera bị che **liên tục hoàn toàn**.

**Điều kiện gán nhãn:**

1. Camera bị che liên tục hoàn toàn, không có đoạn bỏ che xen kẽ.
2. Trạng thái che liên tục kéo dài từ **2 phút (120 giây)** trở lên.
3. Mức che lớn hơn **30% khung hình**.

**Cách xác định thời gian và subvideo:**

- `event_start_time`: thời điểm bắt đầu che liên tục hoàn toàn.
- `event_end_time`: thời điểm kết thúc trạng thái che liên tục hoàn toàn.
- Hệ thống tạo subvideo với 30 giây trước và 30 giây sau khoảng sự kiện, nếu video nguồn còn thời lượng.

**Metadata áp dụng:** chỉ metadata chung. Không lưu `distance_to_camera` hoặc `lighting_condition` cho nhãn này.

### 3.5. `camera_rung_lac`

**Định nghĩa:** camera rung lắc tại chỗ.

**Cách xác định thời gian và subvideo:**

- `event_start_time`: thời điểm camera bắt đầu rung lắc.
- `event_end_time`: thời điểm camera ngừng rung lắc tại chỗ.
- Hệ thống tạo subvideo với 30 giây trước và 30 giây sau khoảng sự kiện, nếu video nguồn còn thời lượng.

**Metadata áp dụng:** chỉ metadata chung. Không lưu `distance_to_camera` hoặc `lighting_condition` cho nhãn này.

### 3.6. `camera_xoay_lech_huong`

**Định nghĩa:** camera xoay sang hướng khác.

**Cách xác định thời gian và subvideo:**

- `event_start_time`: thời điểm camera bắt đầu xoay.
- `event_end_time`: thời điểm camera hoàn tất việc xoay sang hướng khác.
- Hệ thống tạo subvideo với 30 giây trước và 30 giây sau khoảng sự kiện, nếu video nguồn còn thời lượng.

**Metadata áp dụng:** chỉ metadata chung. Không lưu `distance_to_camera` hoặc `lighting_condition` cho nhãn này.

### 3.7. `choi_sang`

**Định nghĩa:** ánh sáng chói làm ảnh hưởng quan sát hình ảnh.

Đây là một nhãn sự kiện do người review xác nhận từ hình ảnh; không phải metadata của nhãn xâm nhập/lảng vảng và không phải technical category do Candidate Mining tự tạo.

**Cách xác định thời gian và subvideo:**

- Không có yêu cầu thời lượng tối thiểu hoặc tối đa.
- Nếu xác định được sự kiện, dùng `event_start_time` và `event_end_time` cho khoảng chói sáng; hệ thống tạo subvideo với 30 giây trước/sau khi video nguồn còn thời lượng.

**Metadata áp dụng:** chỉ metadata chung. Không lưu `distance_to_camera` hoặc `lighting_condition` cho nhãn này.

### 3.8. `nuoc_mua_lam_nhieu_hinh`

**Định nghĩa:** nước mưa, giọt nước hoặc nước vào camera làm nhiễu hình ảnh.

Đây là một nhãn sự kiện do người review xác nhận từ hình ảnh; không phải metadata của nhãn xâm nhập/lảng vảng và không phải technical category do Candidate Mining tự tạo.

**Cách xác định thời gian và subvideo:**

- Không có yêu cầu thời lượng tối thiểu hoặc tối đa.
- Nếu xác định được sự kiện, dùng `event_start_time` và `event_end_time` cho khoảng hình ảnh bị nước/nước mưa làm nhiễu; hệ thống tạo subvideo với 30 giây trước/sau khi video nguồn còn thời lượng.

**Metadata áp dụng:** chỉ metadata chung. Không lưu `distance_to_camera` hoặc `lighting_condition` cho nhãn này.

### 3.9. `normal`

**Định nghĩa:** subvideo bình thường, không có sự kiện thuộc tám nhãn `positive`.

**Metadata áp dụng:** chỉ metadata chung, với:

```text
label = normal
label_group = negative
```

## 4. Metadata chung

Mọi subvideo, không phụ thuộc nhãn, đều lưu schema tối thiểu sau:

```json
{
  "camera_name": "front-gate",
  "video_name": "segment_001.mp4",
  "label": "xam_nhap_hoac_treo_rao",
  "label_group": "positive",
  "event_start_time": 120.0,
  "event_end_time": 145.0,
  "subvideo_start_time": 90.0,
  "subvideo_end_time": 175.0
}
```

| Trường | Mô tả |
|---|---|
| `camera_name` | Tên đại diện camera; có thể tìm theo tên thư mục chứa video. |
| `video_name` | Tên file video nguồn để truy vấn. |
| `label` | Một nhãn duy nhất trong danh mục tại phần 2. |
| `label_group` | `positive` hoặc `negative`. |
| `event_start_time` | Bắt đầu vùng hành vi chính trong video nguồn. |
| `event_end_time` | Kết thúc vùng hành vi chính trong video nguồn. |
| `subvideo_start_time` | Bắt đầu subvideo được trích từ video nguồn. |
| `subvideo_end_time` | Kết thúc subvideo được trích từ video nguồn. |

## 5. Mẫu metadata

### Xâm nhập hoặc trèo rào

```json
{
  "camera_name": "front-gate",
  "video_name": "gate_001.mp4",
  "label": "xam_nhap_hoac_treo_rao",
  "label_group": "positive",
  "event_start_time": 120.0,
  "event_end_time": 145.0,
  "subvideo_start_time": 90.0,
  "subvideo_end_time": 175.0,
  "distance_to_camera": "15m",
  "lighting_condition": "dem_co_den"
}
```

### Lảng vảng gần hàng rào

```json
{
  "camera_name": "side-fence",
  "video_name": "side_001.mp4",
  "label": "lang_vang_gan_hang_rao",
  "label_group": "positive",
  "event_start_time": 60.0,
  "event_end_time": 360.0,
  "subvideo_start_time": 30.0,
  "subvideo_end_time": 390.0,
  "distance_to_camera": "25m",
  "lighting_condition": "ngay"
}
```

### Che camera ngắn

```json
{
  "camera_name": "warehouse-door",
  "video_name": "door_001.mp4",
  "label": "che_camera_ngan",
  "label_group": "positive",
  "event_start_time": 100.0,
  "event_end_time": 240.0,
  "subvideo_start_time": 70.0,
  "subvideo_end_time": 270.0
}
```

### Che camera dài

```json
{
  "camera_name": "warehouse-door",
  "video_name": "door_002.mp4",
  "label": "che_camera_dai",
  "label_group": "positive",
  "event_start_time": 210.0,
  "event_end_time": 330.0,
  "subvideo_start_time": 180.0,
  "subvideo_end_time": 360.0
}
```

### Normal

```json
{
  "camera_name": "parking-lot",
  "video_name": "parking_001.mp4",
  "label": "normal",
  "label_group": "negative",
  "event_start_time": 0.0,
  "event_end_time": 120.0,
  "subvideo_start_time": 0.0,
  "subvideo_end_time": 120.0
}
```

## 6. Checklist

```text
[ ] Mỗi subvideo chỉ có một nhãn.
[ ] Tám nhãn sự kiện có label_group = positive.
[ ] Nhãn normal có label_group = negative.
[ ] Có camera_name và video_name.
[ ] Có event_start_time, event_end_time, subvideo_start_time và subvideo_end_time.
[ ] Xâm nhập/trèo rào có vùng hành vi chính rồi mới thêm 30 giây đầu/cuối.
[ ] Lảng vảng diễn ra ở ngoài khu vực cấm và có bằng chứng tối thiểu 5 phút.
[ ] Che camera ngắn là che/bỏ che ngắt quãng trong chuỗi dài trên 2 phút, che >30% khung hình.
[ ] Che camera dài là che liên tục hoàn toàn >=2 phút, che >30% khung hình.
[ ] distance_to_camera và lighting_condition chỉ có ở xâm nhập/trèo rào và lảng vảng.
[ ] Chói sáng và nước mưa làm nhiễu hình là nhãn positive riêng; không có metadata riêng hoặc yêu cầu thời lượng.
```
