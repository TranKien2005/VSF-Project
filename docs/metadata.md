# Metadata tối giản cho Dataset Camera AI

## 1. Mục tiêu

Đầu vào chỉ là:

```text
1 file video
```

Metadata chỉ giữ những thông tin tối thiểu cần để:

```text
- Biết video nào đang xử lý
- Video có hành vi gì
- Hành vi xảy ra khi nào
- Khoảng cách tới camera nếu hành vi có người
- Hỗ trợ một video có nhiều hành vi
```

---

# 2. Cấu trúc Metadata tối thiểu

```text
video_name
events
```

Trong đó mỗi `event` gồm:

```text
label
start_time
end_time
distance_to_camera
```

Ví dụ:

```json
{
  "video_name": "video_001.mp4",
  "events": [
    {
      "label": "nguoi_treo_rao",
      "start_time": 120.0,
      "end_time": 145.0,
      "distance_to_camera": "15m"
    },
    {
      "label": "xoay_lech_camera",
      "start_time": 200.0,
      "end_time": 230.0,
      "distance_to_camera": null
    }
  ]
}
```

---

# 3. Danh sách Label

## Nhóm 1 — Đột nhập / Trèo rào

### `nguoi_lang_vang`

Ý nghĩa:

```text
Người di chuyển hoặc đứng lâu trong ROI xanh.
Chỉ xác định là lảng vảng khi thời gian > 5 phút.
```

Khoảng cách:

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

---

### `nguoi_tiep_can_hang_rao`

Ý nghĩa:

```text
Người đi vào hoặc chạm ROI vàng sát hàng rào.
```

Khoảng cách:

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

---

### `nguoi_treo_rao`

Ý nghĩa:

```text
Người trèo lên hàng rào, chạm ROI đỏ hoặc vào khu cấm.
```

Khoảng cách:

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

---

# 4. Nhóm 2 — Che camera / Suy giảm hình ảnh

### `che_camera_ngan`

Ý nghĩa:

```text
Camera bị che trong thời gian dưới 2 phút.
```

Khoảng cách:

```text
null
```

---

### `che_camera_dai`

Ý nghĩa:

```text
Camera bị che liên tục từ 2 phút trở lên.
```

Khoảng cách:

```text
null
```

---

### `choi_den_xe`

Ý nghĩa:

```text
Ánh đèn xe quét qua camera gây lóa, sáng hoặc tối hình tạm thời.
```

Khoảng cách:

```text
null
```

---

### `mua_lam_nhieu_hinh`

Ý nghĩa:

```text
Mưa lớn, giọt nước hoặc sương làm nhiễu hoặc nhòe hình ảnh.
```

Khoảng cách:

```text
null
```

---

# 5. Nhóm 3 — Xoay / Rung camera

### `lac_camera_manh`

Ý nghĩa:

```text
Camera rung mạnh làm thay đổi hình ảnh hoặc góc nhìn rõ rệt.
```

Khoảng cách:

```text
null
```

---

### `xoay_lech_camera`

Ý nghĩa:

```text
Camera bị xoay và giữ ở hướng khác so với hướng trước đó.
```

Khoảng cách:

```text
null
```

---

### `rung_nhe_tam_thoi`

Ý nghĩa:

```text
Camera rung nhẹ do gió, phương tiện hoặc tác động nhỏ rồi trở lại bình thường.
```

Khoảng cách:

```text
null
```

---

# 6. Nhóm Chung

### `binh_thuong`

Ý nghĩa:

```text
Video hoạt động bình thường, không có sự kiện bất thường.
```

Khoảng cách:

```text
null
```

---

# 7. Quy tắc khoảng cách

Chỉ các label có người mới cần:

```text
distance_to_camera
```

Áp dụng cho:

```text
nguoi_lang_vang
nguoi_tiep_can_hang_rao
nguoi_treo_rao
```

Giá trị:

```text
5m
10m
15m
20m
25m
30m
35m
40m
unknown
```

Các label khác:

```text
distance_to_camera = null
```

---

# 8. Quy tắc nhiều hành vi trong một video

Một video có thể có nhiều event.

Ví dụ:

```json
{
  "video_name": "video_002.mp4",
  "events": [
    {
      "label": "nguoi_tiep_can_hang_rao",
      "start_time": 60.0,
      "end_time": 90.0,
      "distance_to_camera": "20m"
    },
    {
      "label": "nguoi_treo_rao",
      "start_time": 85.0,
      "end_time": 120.0,
      "distance_to_camera": "20m"
    }
  ]
}
```

Không giả định:

```text
1 video = 1 label
```

---

# 9. Metadata cấp Clip Output

Mỗi clip output chỉ cần:

```text
clip_name
source_video
labels
start_time
end_time
distance_to_camera
```

Ví dụ:

```json
{
  "clip_name": "clip_0001.mp4",
  "source_video": "video_002.mp4",
  "labels": [
    "nguoi_tiep_can_hang_rao",
    "nguoi_treo_rao"
  ],
  "start_time": 60.0,
  "end_time": 120.0,
  "distance_to_camera": "20m"
}
```

Một clip có thể có nhiều label.

---

# 10. Quy tắc đặc biệt

## Lảng vảng

```text
Thời gian > 5 phút
→ nguoi_lang_vang
```

Không dùng clip 60 giây để chứng minh riêng hành vi lảng vảng.

---

## Che camera

```text
< 2 phút
→ che_camera_ngan

>= 2 phút
→ che_camera_dai
```

---

# 11. Checklist cho Dev

```text
[ ] Input chỉ cần video_name.
[ ] Một video có thể có nhiều event.
[ ] Mỗi event có label, start_time, end_time.
[ ] Chỉ 3 label có người mới có distance_to_camera.
[ ] Các label khác để distance_to_camera = null.
[ ] Lảng vảng chỉ xác định khi > 5 phút.
[ ] Che camera chia ngắn < 2 phút và dài >= 2 phút.
[ ] Không cần lưu các chỉ số CV kỹ thuật vào metadata chính thức.
[ ] Các chỉ số như blur score, brightness, motion score chỉ dùng nội bộ để detect.
```
