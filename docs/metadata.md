# Metadata output cho gán nhãn người review

> **Status: specification for the separate human-labeling workflow.** Schema này không phải `technical-candidate.v2` hiện tại của Candidate Mining.

Mỗi output label data đại diện cho một subvideo và một nhãn sự kiện duy nhất.

## Trường chung

```json
{
  "camera_name": "front-gate",
  "video_name": "gate_001.mp4",
  "label": "choi_sang",
  "label_group": "positive",
  "event_start_time": 120.0,
  "event_end_time": 145.0,
  "subvideo_start_time": 90.0,
  "subvideo_end_time": 175.0
}
```

| Trường | Ý nghĩa |
|---|---|
| `camera_name` | Tên camera, có thể lấy từ thư mục camera chứa video. |
| `video_name` | Tên video nguồn. |
| `label` | Một nhãn trong [huong-dan-gan-nhan.md](huong-dan-gan-nhan.md). |
| `label_group` | `positive` cho nhãn sự kiện; `negative` cho `normal`. |
| `event_start_time`, `event_end_time` | Khoảng sự kiện trong video nguồn, theo giây. |
| `subvideo_start_time`, `subvideo_end_time` | Khoảng subvideo được trích, theo giây. |

## Metadata chỉ cho nhãn liên quan người

Chỉ `xam_nhap_hoac_treo_rao` và `lang_vang_gan_hang_rao` có hai trường thêm:

```json
{
  "distance_to_camera": "15m",
  "lighting_condition": "dem_co_den"
}
```

- `distance_to_camera`: `5m`, `10m`, `15m`, `20m`, `25m`, `30m`, `35m`, `40m`.
- `lighting_condition`: `ngay`, `dem_co_den`, `dem_khong_den`.

Các nhãn `che_camera_ngan`, `che_camera_dai`, `camera_rung_lac`, `camera_xoay_lech_huong`, `choi_sang`, `nuoc_mua_lam_nhieu_hinh` và `normal` chỉ dùng trường chung.

Đặc biệt, `choi_sang` và `nuoc_mua_lam_nhieu_hinh` là **giá trị nhãn**, không phải metadata/condition. Hai nhãn này không có metadata riêng và không có điều kiện thời lượng.

## Quy tắc thời gian

- Chỉ `lang_vang_gan_hang_rao` yêu cầu `event_end_time - event_start_time >= 300` giây.
- Quy tắc che camera ngắn/dài được áp dụng riêng cho hai nhãn che camera theo [hanh-vi.md](hanh-vi.md).
- `choi_sang` và `nuoc_mua_lam_nhieu_hinh` không có thời lượng tối thiểu/tối đa; lưu event bounds khi người review xác định được.
