# VSF Project — AI Camera Test Data Preparation

Repository này hỗ trợ nhóm chuẩn bị dữ liệu kiểm thử và ground truth cho bài toán AI Camera an ninh vành đai.

> Model AI đã có sẵn và nằm ngoài phạm vi repository này. Repository không dùng để huấn luyện, thay đổi hoặc đánh giá lại model. Mục tiêu là tạo candidate review queue, công cụ annotation, manifest dữ liệu và artifact bàn giao có thể truy vết.

## Phân công

| Vai trò | Phụ trách | Phạm vi |
|---|---|---|
| A — QA Lead / Test Design | A | Use case, coverage, checklist bàn giao và review đầu ra |
| B — Data & Automation | B | Video inventory, candidate mining, sampling, proxy clip, manifest và pipeline tái lập |
| C — Annotation & Data Quality | C | Annotation tool, taxonomy nhãn, gán nhãn, review và ground truth |

## Luồng làm việc

```text
Raw video
  ↓ B: inventory + candidate mining + sampling
Candidate manifest + proxy clips
  ↓ C: annotation tool + human review
Annotation / ground truth
  ↓ A: coverage + kiểm tra artifact bàn giao
Versioned test-data package
```

## Quy tắc cắt proxy clip

| Loại candidate | Nội dung proxy clip |
|---|---|
| Các event thông thường | 30 giây trước event + thời lượng event + 30 giây sau event; tự cắt theo biên video |
| Lảng vảng gần khu vực/hàng rào | Cửa sổ liên tục đủ 5 phút tính từ thời điểm đối tượng vào vùng theo dõi; nếu video/context không đủ, ghi `insufficient_context` |
| Random background | Clip nền ngẫu nhiên, không giao với candidate event theo exclusion window đã cấu hình |

Candidate do pipeline tạo ra chỉ là **gợi ý để review**, không phải ground truth và không được dùng để kết luận KPI/model.

## Cấu trúc thư mục

```text
.
├── apps/
│   ├── candidate-mining/          # B phụ trách
│   │   ├── src/candidate_mining/  # Mã Python pipeline
│   │   └── tests/                 # Unit/integration tests của pipeline
│   └── annotation-tool/           # C phụ trách: UI và logic gán nhãn
│
├── shared/
│   ├── schemas/                   # Data contract JSON Schema giữa B và C
│   └── label-taxonomy.json        # Taxonomy nhãn do C quản lý, A review
│
├── configs/                       # Cấu hình local: sampling, merge gap, clip duration
├── scripts/                       # Script chạy local trên Windows
│
├── data/                          # Không commit video hoặc output nhạy cảm
│   ├── raw/                       # Video thô đầu vào
│   ├── inventory/                 # Video inventory/checksum
│   ├── manifests/                 # Candidate event và annotation export
│   └── review_queue/
│       ├── candidates/            # Proxy clips event thường
│       ├── loitering/             # Proxy clips 5 phút cho lảng vảng
│       └── random_background/     # Background sample cho human review
│
├── outputs/
│   ├── logs/                      # Log runtime
│   └── reports/                   # Báo cáo mining/quality không nhạy cảm
│
├── docs/                          # Tài liệu nghiệp vụ, contract và hướng dẫn
├── ke-hoach-3-tuan-kiem-thu-ai-camera.md
└── README.md
```

## Data contract B → C

B xuất proxy clip và candidate manifest. Mỗi record cần có ít nhất:

```text
sample_id
source_id
source_path
camera_id
clip_path
clip_start_sec
clip_end_sec
candidate_type
candidate_start_sec
candidate_end_sec
selection_source
review_status
```

- Tất cả timestamp `*_sec` tính theo giây từ đầu **video nguồn**.
- `sample_id` là khóa duy nhất để C trả annotation và để A truy vết artifact.
- Nếu không biết trường nào ở raw video, dùng `unknown` thay vì tự suy diễn.

C trả annotation liên kết qua `sample_id` với các trường tối thiểu:

```text
sample_id
event_label
event_start_sec
event_end_sec
ground_truth_status
reviewer
comment
```

## Git và dữ liệu nhạy cảm

Không commit/push các thư mục sau:

```text
data/raw/
data/inventory/
data/manifests/
data/review_queue/
outputs/logs/
```

Video camera có thể chứa mặt người, biển số hoặc thông tin vận hành. Chỉ commit code, schema, cấu hình không nhạy cảm, tài liệu và test fixture đã được phép sử dụng.

## Bước tiếp theo

1. B: đặt một video thô vào `data/raw/` hoặc cung cấp đường dẫn local.
2. B: tạo candidate-mining POC nhận một video và xuất inventory, manifest, proxy clips, random background samples.
3. C: hoàn thiện annotation tool và thống nhất schema/`sample_id` với B.
4. A: review coverage, artifact và checklist bàn giao.
