# Kế hoạch Candidate Mining v1 — Vai trò B (Data & Automation)

> **Mục đích:** từ video thô, tạo các đoạn video mẫu (*sample/proxy clip*) để C review và gán nhãn. Pipeline này chỉ tìm **candidate**; không kết luận xâm nhập, che camera, camera rung hay chất lượng model.

---

## 1. Phạm vi công việc của B

Model AI nghiệp vụ đã do nhóm AI hoàn thành. B **không phát triển, thay đổi hoặc test lại model đó**.

B xây dựng pipeline để:

1. Đọc video thô và tạo inventory kỹ thuật.
2. Tìm các đoạn có người xuất hiện.
3. Tìm các đoạn nghi camera bị che.
4. Tìm các đoạn nghi camera bị rung/lệch góc.
5. Cắt clip có đủ ngữ cảnh để C review.
6. Xuất manifest chung để C dùng annotation tool gán đa nhãn.
7. Lấy thêm clip nền ngẫu nhiên để không chỉ review các đoạn do tool chọn.

---

## 2. Ý nghĩa dữ liệu đầu ra

Các folder sau là **nhóm candidate để review**, không phải nhãn ground truth.

```text
data/review_queue/
├── person_detected/       # Tool nhìn thấy người trong frame
├── camera_cover/          # Tool thấy tín hiệu nghi camera bị che
├── camera_movement/       # Tool thấy tín hiệu nghi camera rung/xoay/lệch
└── random_background/     # Clip nền lấy ngẫu nhiên
```

| Folder | Khẳng định được | Không được khẳng định |
|---|---|---|
| `person_detected/` | Có frame chứa người theo detector | Người trèo rào, xâm nhập ROI, lảng vảng, mức cảnh báo |
| `camera_cover/` | Có tín hiệu hình ảnh nghi che camera | Camera chắc chắn bị che có chủ đích |
| `camera_movement/` | Có tín hiệu nghi global scene/camera thay đổi | Camera chắc chắn bị rung hoặc xoay lệch |
| `random_background/` | Mẫu được chọn ngẫu nhiên theo rule | Không có event |

C là người xem clip và quyết định nhãn cuối cùng, có thể gán **nhiều nhãn cho một sample**.

---

## 3. Nguyên tắc đa category, một sample

Một đoạn có thể đồng thời có người, che camera và rung camera. Ví dụ người đưa vật che lens làm camera rung.

- Đoạn đó được gắn cả ba category trong manifest.
- Khi cần thuận tiện review, có thể xuất clip vào nhiều folder category.
- Nhưng về dữ liệu logic, đoạn đó chỉ là **một `sample_id` duy nhất**.
- C gán nhãn một lần theo `sample_id`, không gán lại ba lần chỉ vì clip xuất hiện ở ba folder.

Ví dụ:

```csv
sample_id,source_id,categories
cam01_000320_000410,video_01,"person_detected|camera_cover|camera_movement"
```

---

## 4. Luồng pipeline v1

```text
Raw video
  ↓
Inventory: metadata, duration, FPS, resolution, codec, checksum
  ↓
Frame sampling
  ├─ YOLO nano: phát hiện person
  ├─ Visual heuristic: nghi cover
  └─ Global motion / feature displacement: nghi camera movement
  ↓
Danh sách timestamp signal theo từng category
  ↓
Gộp timestamp gần nhau thành segment
  ↓
Tạo sample/proxy clip
  ↓
Xuất folder review queue + candidate_events.csv
  ↓
C review/gán nhãn bằng annotation tool
```

---

## 5. Phương pháp candidate theo từng nhóm

### 5.1. `person_detected`

**Mục tiêu:** tìm đoạn có người để C review; không suy luận hành vi xâm nhập.

- Dùng YOLO pretrained bản nano để phát hiện class `person`.
- Frame nào có ít nhất một person detection đạt confidence threshold được ghi timestamp signal.
- Không cần ROI ở pipeline v1.
- Không gọi đây là `intrusion` vì detector chưa biết người có ở ROI hay có trèo rào không.

### 5.2. `camera_cover`

**Mục tiêu:** tìm đoạn nghi che camera bằng tín hiệu kỹ thuật, chưa cần model chuyên biệt ở v1.

Các heuristic khởi điểm:

- brightness giảm/tăng đột ngột;
- tỷ lệ pixel tối/đồng nhất bất thường;
- edge/detail giảm mạnh;
- blur tăng mạnh;
- histogram thay đổi lớn và kéo dài.

Mưa, sương, low light hoặc chói đèn xe có thể cũng tạo tín hiệu. Những clip này vẫn được xuất để C phân biệt khi gán nhãn.

### 5.3. `camera_movement`

**Mục tiêu:** tìm đoạn nghi toàn bộ khung hình dịch chuyển/rung/lệch.

Các heuristic khởi điểm:

- optical flow toàn cục;
- feature matching giữa các frame liên tiếp;
- global frame displacement;
- scene-consistency change kéo dài.

Rung do gió, xe hoặc thay đổi cảnh không đồng nghĩa camera bị xoay. Pipeline chỉ tạo candidate để review.

### 5.4. `random_background`

- Lấy clip ngẫu nhiên trải đều trong video.
- Loại các đoạn giao với cửa sổ loại trừ quanh candidate event.
- Mục đích: có normal/negative thực tế và phát hiện event pipeline có thể đã bỏ sót.

---

## 6. Từ frame signal thành một sample

Không tạo một clip cho từng frame có tín hiệu.

### 6.1. Quy tắc gộp segment

Ví dụ pipeline lấy mẫu 2 FPS:

```text
00:01:00.5  có person
00:01:01.0  có person
...
00:01:40.0  có person
```

Các frame trên được gộp thành một person segment:

```text
event_start_sec = 60.5
event_end_sec   = 100.0
```

Nếu detector mất dấu ngắn:

```text
00:01:00 → 00:01:40  có person
00:01:41 → 00:01:44  không có person
00:01:45 → 00:02:20  có person
```

Khi khoảng cách mất tín hiệu nhỏ hơn `merge_gap_seconds` (cấu hình khởi điểm 5–10 giây), gộp thành một segment. Nếu lớn hơn ngưỡng, tạo segment/sample mới.

Lý do: detector có thể bỏ sót một vài frame do che khuất, ánh sáng hoặc vật cản.

### 6.2. Quy tắc cắt proxy clip

Với tất cả segment candidate:

```text
clip_start = max(0, event_start - 30 giây)
clip_end   = min(video_duration, event_end + 30 giây)
```

Tức clip gồm:

```text
30 giây trước + toàn bộ thời lượng segment + 30 giây sau
```

Nếu event gần đầu/cuối video, cắt tới biên video và ghi `context_status` phù hợp.

### 6.3. Quy tắc về lảng vảng 5 phút

Không có folder `loitering` trong candidate mining v1.

- Ngưỡng **5 phút** là rule phát hiện/cảnh báo nghiệp vụ của hệ thống/model.
- B không tự kết luận đối tượng lảng vảng.
- Nếu YOLO nhận ra người liên tục trong 7 phút, B giữ **toàn bộ person segment 7 phút**, cộng 30 giây trước/sau.
- C hoặc xử lý nghiệp vụ sau này mới dùng thời lượng segment để xác định có đạt ngưỡng 5 phút hay không.

---

## 7. Manifest chung B → C

File chính:

```text
data/manifests/candidate_events.csv
```

Schema v1:

```csv
sample_id,source_id,source_path,camera_id,clip_path,clip_start_sec,clip_end_sec,categories,candidate_start_sec,candidate_end_sec,selection_source,person_count_max,motion_score,brightness_score,blur_score,camera_shift_score,context_status,review_status
```

Ý nghĩa trường tối thiểu:

| Field | Ý nghĩa |
|---|---|
| `sample_id` | Khóa duy nhất của sample, dùng để nối annotation của C |
| `source_id` | ID video nguồn |
| `source_path` | Đường dẫn local video nguồn; không đưa lên GitHub |
| `camera_id` | ID camera; chưa biết dùng `unknown` |
| `clip_path` | Đường dẫn proxy clip |
| `clip_start_sec`, `clip_end_sec` | Khoảng thời gian clip tính từ đầu video nguồn |
| `categories` | Một hoặc nhiều candidate category, ngăn cách bằng `|` |
| `candidate_start_sec`, `candidate_end_sec` | Segment do pipeline phát hiện, tính từ đầu video nguồn |
| `selection_source` | `tool_selected` hoặc `random_background` |
| Các trường `*_score` | Score/feature kỹ thuật phục vụ debug, không phải nhãn |
| `context_status` | `sufficient`, `clipped_at_video_start`, `clipped_at_video_end` |
| `review_status` | Khởi tạo là `pending_review` |

Ví dụ:

```csv
cam01_000320_000410,video_01,D:\\videos\\video_01.mp4,unknown,data/review_queue/person_detected/cam01_000320_000410.mp4,290,440,"person_detected|camera_movement",320,410,tool_selected,1,0.88,0.04,0.12,0.81,sufficient,pending_review
```

Tất cả trường `*_sec` luôn tính từ đầu **video nguồn**, không tính riêng từ đầu proxy clip.

---

## 8. Contract annotation C → B/A

Tool của C đọc `sample_id` và trả annotation có ít nhất:

```csv
sample_id,event_label,event_start_sec,event_end_sec,ground_truth_status,reviewer,comment
```

- C có thể trả nhiều record cùng `sample_id` để gán đa nhãn/nhiều event.
- `event_start_sec`/`event_end_sec` phải quy đổi về giây từ đầu video nguồn.
- B không sửa nhãn của C; B chỉ validate schema, source mapping và dữ liệu thời gian.

---

## 9. Cấu trúc folder áp dụng

```text
data/
├── raw/                         # Video gốc, không commit
├── inventory/                   # Inventory/checksum, không commit
├── manifests/                   # candidate_events.csv, không commit
└── review_queue/
    ├── person_detected/
    ├── camera_cover/
    ├── camera_movement/
    └── random_background/
```

> Các folder trên đang có thể khác cấu trúc placeholder cũ. Khi bắt đầu code, cập nhật `.gitignore` và `README.md` để thống nhất; không cần tạo folder `loitering`, `mixed_or_uncertain` hoặc `insufficient_context`.

---

## 10. Definition of Done POC v1

Với một video MP4/H.264 đầu vào, chạy POC local trên RTX 4060 Laptop phải tạo được:

- một row inventory gồm metadata kỹ thuật và checksum;
- candidate manifest CSV;
- proxy clip trong `person_detected/` khi detector thấy người;
- proxy clip trong `camera_cover/` hoặc `camera_movement/` khi heuristic phát tín hiệu;
- random background clips;
- mỗi sample truy vết được về video nguồn, segment timestamp và các category;
- README/câu lệnh tái chạy trên video khác.

POC v1 **không** có mục tiêu:

- kết luận xâm nhập/trèo rào/lảng vảng;
- vẽ hoặc sửa ROI;
- tính KPI model;
- tạo ground truth tự động;
- khẳng định candidate là event thật.
