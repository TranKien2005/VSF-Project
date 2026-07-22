# Yêu cầu và hướng dẫn sử dụng tool gán nhãn

> **Status: specification for a separate labeling tool.** This tool and its output-label persistence/export workflow are not implemented by the current Candidate Mining GUI.

## 1. Mục đích và phạm vi

Tool gán nhãn dùng để xem video camera, xem các subvideo gợi ý từ thư mục `data`, tạo/chỉnh sửa/xóa output label data và export dữ liệu đã gán nhãn.

Subvideo đầu vào chỉ là **gợi ý để review**. Output label data do người dùng tạo là dữ liệu gán nhãn độc lập:

- output label data không bắt buộc có số lượng bằng số subvideo;
- thời gian của output label data có thể khác thời gian subvideo gợi ý;
- một hoặc nhiều subvideo có thể dẫn đến một output label data;
- một subvideo có thể không tạo output label data nếu người review xác định không có sự kiện cần gán nhãn;
- người review phải dùng video gốc để xác nhận sự kiện, không chỉ dựa trên subvideo.

Các nhãn, điều kiện thời gian và metadata phải theo [huong-dan-gan-nhan.md](huong-dan-gan-nhan.md).

## 2. Dữ liệu đầu vào và cấu trúc hiển thị

Tool lấy thông tin từ thư mục `data` và dựng cây dữ liệu phân tầng theo camera:

```text
Camera
└── Video
    └── Subvideo gợi ý
```

- **Camera** là nhóm video cùng camera.
- **Video** là video gốc thuộc camera đó.
- **Subvideo** là đoạn gợi ý để người review xem xét, ví dụ subvideo liên quan person detection hoặc camera anomaly.

Cây dữ liệu đầu vào nằm ở vùng bên trái của giao diện. Cây này dùng để duyệt video gốc và subvideo gợi ý; không phải là danh sách output label data.

### 2.1. Khi chọn video

Khi chọn một video trong cây bên trái, tool phải:

1. load video gốc đó vào player;
2. hiển thị timeline của toàn bộ video gốc;
3. cho phép xem video theo thời gian của video gốc;
4. không tự gán nhãn hoặc tự tạo output label data chỉ vì video/subvideo được chọn.

### 2.2. Khi chọn subvideo

Khi chọn một subvideo trong cây bên trái, tool phải:

1. load video gốc chứa subvideo đó;
2. đánh dấu thời điểm bắt đầu và kết thúc của subvideo trên timeline video gốc;
3. hiển thị rõ khoảng subvideo trên timeline;
4. bắt đầu phát từ đầu subvideo;
5. chỉ phát trong khoảng từ điểm bắt đầu đến điểm kết thúc của subvideo.

Timeline phải luôn hiển thị:

- thời gian hiện tại của video đang phát;
- thời lượng/timeline của video gốc;
- điểm bắt đầu và điểm kết thúc đã đánh dấu của subvideo đang chọn;
- thời gian của hai điểm đánh dấu đó.

## 3. Khu vực tạo output label data

Bên phải giao diện có sidebar để tạo hoặc chỉnh sửa **output label data**.

### 3.1. Các trường được tạo tự động

Khi người dùng đang xem video/subvideo, tool tự điền các trường sau từ dữ liệu nguồn:

```text
camera_name
video_name
```

Người dùng không cần tự nhập hai trường này.

### 3.2. Các trường người dùng nhập/chọn

Sidebar phải cho phép người dùng nhập hoặc chọn:

```text
event_start_time
event_end_time
label
```

- `event_start_time`: thời điểm bắt đầu sự kiện trong video gốc.
- `event_end_time`: thời điểm kết thúc sự kiện trong video gốc.
- `label`: một loại nhãn theo tài liệu hướng dẫn gán nhãn.

Sau khi người dùng chọn nhãn, sidebar chỉ hiển thị những metadata tương ứng với nhãn đó. Metadata phải được trình bày bằng danh sách chọn hoặc checkbox theo loại dữ liệu để người dùng chọn trực tiếp, không phải tự gõ tự do khi đã có tập giá trị quy định.

### 3.3. Metadata hiển thị theo nhãn

| Nhãn | Metadata riêng cần hiển thị |
|---|---|
| `xam_nhap_hoac_treo_rao` | `distance_to_camera`, `lighting_condition` |
| `lang_vang_gan_hang_rao` | `distance_to_camera`, `lighting_condition` |
| `che_camera_ngan` | Không có metadata riêng; chỉ dùng metadata chung. |
| `che_camera_dai` | Không có metadata riêng; chỉ dùng metadata chung. |
| `camera_rung_lac` | Không có metadata riêng; chỉ dùng metadata chung. |
| `camera_xoay_lech_huong` | Không có metadata riêng; chỉ dùng metadata chung. |
| `choi_sang` | Không có metadata riêng; chỉ dùng metadata chung. |
| `nuoc_mua_lam_nhieu_hinh` | Không có metadata riêng; chỉ dùng metadata chung. |
| `normal` | Không có metadata riêng; chỉ dùng metadata chung. |

Với hai nhãn liên quan người (`xam_nhap_hoac_treo_rao`, `lang_vang_gan_hang_rao`), tool phải cho chọn:

```text
distance_to_camera:
5m, 10m, 15m, 20m, 25m, 30m, 35m, 40m

lighting_condition:
ngay, dem_co_den, dem_khong_den

```

`choi_sang` và `nuoc_mua_lam_nhieu_hinh` là hai nhãn `positive` riêng trong danh sách nhãn. Khi người dùng chọn hai nhãn này, tool chỉ hiển thị metadata chung; không hiển thị trường metadata đặc biệt và không kiểm tra thời lượng tối thiểu.

### 3.4. Kiểm tra nhãn lảng vảng

Khi chọn `lang_vang_gan_hang_rao`, tool phải kiểm tra:

```text
event_end_time - event_start_time >= 5 phút (300 giây)
```

Nếu thời lượng chưa đủ 5 phút, không được cho lưu output label data với nhãn lảng vảng.

## 4. Lưu, xem, chỉnh sửa và xóa output label data

### 4.1. Lưu

Sidebar có nút **Save** để lưu output label data.

Khi lưu thành công:

1. dữ liệu được lưu cùng camera, video, nhãn, thời gian và metadata đã chọn;
2. output label data mới xuất hiện trong cây dữ liệu đầu ra ở bên phải;
3. dữ liệu đầu ra không thay thế hoặc sửa subvideo gợi ý ở cây bên trái.

### 4.2. Cây output label data

Bên phải có một hệ thống phân tầng riêng cho output label data:

```text
Camera
└── Video
    └── Output label data
```

Cây bên phải không hiển thị subvideo gợi ý. Nó chỉ hiển thị các output label data đã được lưu.

Khi chọn một output label data trong cây bên phải, tool phải:

1. load video gốc tương ứng;
2. đánh dấu và phát khoảng thời gian của output label data tương tự cách load subvideo;
3. điền dữ liệu đã lưu vào sidebar để người dùng xem hoặc chỉnh sửa;
4. cho phép sửa các thời gian, loại nhãn và metadata tương ứng;
5. cho phép bấm **Save** để lưu lại phiên bản đã chỉnh sửa.

### 4.3. Xóa

Khi chọn một output label data trong cây bên phải, có nút **Delete** để xóa output label data đang chọn.

Nút xóa chỉ xóa output label data; không xóa video nguồn, camera, subvideo gợi ý hoặc dữ liệu đầu vào.

## 5. Export output label data

Tool có một tab **Export**.

Tab này có nút **Export all** để export toàn bộ output label data đã lưu.

Khi người dùng nhấn Export all, tool phải mở Explorer để người dùng chọn vị trí lưu. Tool export theo metadata của output label data và theo cấu trúc thư mục:

```text
<selected-export-folder>/
└── <camera_name>/
    └── positive/ hoặc negative/
        └── <nhom-nhan-theo-dieu-kien>/
            └── <distance>/                 # chỉ xâm nhập hoặc lảng vảng
                └── <subvideo-output>
```

Quy tắc các tầng export:

1. **`camera_name`**: tên camera của output label data.
2. **`positive` hoặc `negative`**: lấy từ `label_group`.
3. **`nhom-nhan-theo-dieu-kien`**: tên nhãn kết hợp với điều kiện phù hợp. Ví dụ:

```text
xam_nhap_hoac_treo_rao_ngay
xam_nhap_hoac_treo_rao_dem_co_den
lang_vang_gan_hang_rao_ngay
choi_sang
nuoc_mua_lam_nhieu_hinh
```

4. **`distance`**: chỉ dành cho `xam_nhap_hoac_treo_rao` và `lang_vang_gan_hang_rao`, lấy từ `distance_to_camera`.

Các nhãn không liên quan xâm nhập/lảng vảng không có tầng `distance`.

Ví dụ:

```text
export/
└── front-gate/
    └── positive/
        └── xam_nhap_hoac_treo_rao_dem_co_den/
            └── 15m/
                └── <subvideo-output>
```

```text
export/
└── warehouse-door/
    └── positive/
        └── che_camera_dai/
            └── <subvideo-output>
```

```text
export/
└── parking-lot/
    └── negative/
        └── normal/
            └── <subvideo-output>
```

## 6. Hướng dẫn review dữ liệu

### 6.1. Kiểm tra đầu và cuối subvideo

Nhiều subvideo nguồn có thể bị mất một phần do điều kiện ghi hình hoặc bị che. Khi review, phải kiểm tra đầu và cuối của từng subvideo, không chỉ xem phần giữa đoạn.

### 6.2. Chuỗi subvideo person detection gần nhau

Nhiều subvideo liên quan person detection có thể xuất hiện gần nhau về thời gian và cùng thuộc một chuỗi hành vi. Khi gặp các subvideo gần nhau, nên xem video gốc từ đầu đến cuối toàn bộ chuỗi đó trước khi tạo output label data.

Không coi mỗi subvideo person detection là một event độc lập một cách máy móc.

### 6.3. Subvideo camera anomaly

Với subvideo camera anomaly, chỉ review để gán các nhãn:

```text
che_camera_ngan
che_camera_dai
camera_rung_lac
camera_xoay_lech_huong
choi_sang
nuoc_mua_lam_nhieu_hinh
```

Chói sáng và nước mưa làm nhiễu hình là nhãn do người review quyết định từ nội dung video; không phải metadata và không được suy ra tự động từ technical candidate `camera_anomaly`. Hai nhãn này không có metadata riêng hoặc yêu cầu thời lượng.

### 6.4. Subvideo person detection

Với subvideo person detection, quan sát video rõ ràng để xác nhận nhãn liên quan người:

```text
xam_nhap_hoac_treo_rao
lang_vang_gan_hang_rao
```

Chói sáng hoặc nước mưa làm nhiễu hình phải được tạo thành output label data với nhãn riêng khi người review xác nhận; chúng không được lưu như metadata của nhãn person detection.

## 7. Tham khảo tab Review của Candidate Mining GUI

Phần review của tool gán nhãn nên tham khảo cách làm việc của tab **Review** trong Candidate Mining GUI hiện có. Đây là tham khảo về cách xem technical candidate/subvideo và timeline, không phải quy tắc tự động gán nhãn.

Các điểm cần tham khảo:

- Tab Review hiển thị danh sách candidate/subvideo kỹ thuật ở một panel riêng và vùng xem video ở bên cạnh.
- Khi chọn một candidate, GUI load **video gốc** tương ứng thay vì chỉ mở một file clip độc lập.
- Khoảng context của candidate được đánh dấu trực tiếp trên timeline video gốc bằng hai mốc **START** và **END**.
- Timeline hiển thị thời gian hiện tại, thời lượng video và thời gian của hai mốc context; vùng context được highlight để người review nhận biết đoạn đang xem.
- Playback của candidate bị giới hạn trong khoảng context: bắt đầu ở mốc START và dừng/loop trong phạm vi END, thay vì chạy vượt qua đoạn đang review.
- Bbox kỹ thuật và ROI có thể được overlay để tham khảo, nhưng không phải nhãn cuối cùng. Người review vẫn phải xem nội dung video và quyết định output label data.
- Candidate/subvideo chỉ cung cấp context review. Khi cần, người review phải xem thêm phần trước/sau trên video gốc để xác định đúng `event_start_time` và `event_end_time`.

Tool gán nhãn mới cần áp dụng cùng nguyên tắc khi chọn cả subvideo gợi ý ở cây bên trái lẫn output label data đã lưu ở cây bên phải: load video gốc, highlight start/end trên timeline, phát trong khoảng được chọn và hiển thị thời gian hiện tại cùng hai mốc đánh dấu.

## 8. Quy trình sử dụng đề xuất

1. Mở tool; tool đọc thư mục `data` và hiển thị cây Camera → Video → Subvideo ở bên trái.
2. Chọn video để xem toàn bộ video gốc, hoặc chọn subvideo để load video gốc và phát đúng đoạn đã được đánh dấu trên timeline.
3. Kiểm tra đầu/cuối subvideo. Với subvideo person detection gần nhau, xem cả chuỗi trên video gốc.
4. Xác định event thực tế; không bắt buộc output label data phải trùng số lượng hoặc thời gian của subvideo gợi ý.
5. Nhập `event_start_time`, `event_end_time` và chọn `label` ở sidebar.
6. Chọn metadata mà sidebar hiển thị cho nhãn đã chọn.
7. Nếu là lảng vảng, kiểm tra sự kiện có thời lượng từ 5 phút trở lên trước khi lưu.
8. Nhấn Save. Output label data xuất hiện trong cây Camera → Video → Output label data bên phải.
9. Chọn output label data đã lưu để xem lại, chỉnh sửa và Save lại; nếu không cần thì chọn Delete để xóa riêng output label data đó.
10. Mở tab Export, nhấn Export all, chọn thư mục đích bằng Explorer và export toàn bộ output label data theo cấu trúc camera → positive/negative → nhãn theo điều kiện → distance khi áp dụng.
