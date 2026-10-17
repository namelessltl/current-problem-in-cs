# Giải N-Queens bằng SAT, CP và ILP

Dự án tìm **một nghiệm khả thi** của bài toán đặt N quân hậu trên bàn cờ N × N sao cho không có hai hậu cùng hàng, cột hoặc đường chéo. Chương trình so sánh năm encoding SAT tự cài đặt và bốn solver đối chứng CP/ILP.

## 1. Cấu trúc mã nguồn

| File | Vai trò |
|---|---|
| `binomial.py` | Encoding Pairwise (Binomial), cấm từng cặp biến cùng đúng |
| `binary.py` | Encoding Binary và phần dùng chung cho Commander/Product |
| `sequential.py` | Encoding Sequential Counter |
| `commander.py` | Commander kết hợp Binary/Pairwise trong nhóm |
| `product.py` | Product kết hợp Binary/Pairwise trên các biến hàng/cột phụ |
| `comparison_solvers.py` | Mô hình CP-SAT, CPLEX CP, CPLEX MIP, Gurobi MIP và kiểm tra nghiệm |
| `playground.py` | Tạo bài toán SAT, chạy benchmark, áp dụng timeout và xuất CSV |
| `requirements-comparison.txt` | Các thư viện cho solver đối chứng |
| `results/` | Số liệu thô, cấu hình thực nghiệm và log |

**Phạm vi bản hiện tại:** năm encoding SAT được viết thủ công; PySAT được dùng để gọi Glucose3.

## 2. Cài đặt môi trường

Các lệnh dưới đây chạy trong **PowerShell**, tại thư mục gốc dự án. Cần Python 64-bit và các phiên bản thư viện hỗ trợ Python đang sử dụng. Môi trường phát triển hiện tại dùng Python 3.14; phiên bản cụ thể của mỗi lượt chạy được lưu trong metadata.

### Tạo môi trường ảo

Nếu chưa có `.venv`:

```powershell
python -m venv .venv
```

Dùng đường dẫn Python của môi trường ảo trong tất cả lệnh để tránh chạy nhầm Python hệ thống; không bắt buộc kích hoạt môi trường.

### Cài thư viện

```powershell
.\.venv\Scripts\python.exe -m pip install python-sat
.\.venv\Scripts\python.exe -m pip install -r requirements-comparison.txt
```


## 3. Kiểm chứng trước khi thực nghiệm

Chạy thử SAT với các trường hợp có và không có nghiệm:

```powershell
.\.venv\Scripts\python.exe playground.py --methods Sequential Binomial Binary Commander Product --sizes 1 2 3 4 8 --timeout 20 --threads 1 --repeats 1 --output results/sat_validation.csv
```

Kết quả mong đợi cho mỗi phương pháp:

| N | Trạng thái |
|---|---|
| 1 | SAT |
| 2, 3 | UNSAT |
| 4, 8 | SAT |

Chương trình tự kiểm tra mỗi nghiệm SAT: đúng N quân hậu, mỗi hàng/cột có một hậu và không trùng đường chéo. Nghiệm sai sẽ được ghi `ERROR`. Cột `valid` phải là `True` ở mọi dòng `SAT`.


Sau khi cấu hình đủ solver đối chứng:

```powershell
.\.venv\Scripts\python.exe playground.py --methods CP-SAT CPLEX-CP CPLEX-MIP Gurobi-MIP --sizes 1 2 3 4 8 --timeout 20 --threads 1 --repeats 1 --output results/<ten_file.csv>
```

Kỳ vọng 20 dòng với trạng thái theo bảng trên. Xử lý `ERROR`/`UNAVAILABLE` trước khi chạy thí nghiệm lớn. Kiểm tra này kiểm chứng các trường hợp nhỏ, không thay thế chứng minh tính đúng tổng quát của encoding. 

## 4. Chạy thực nghiệm

Chạy **lần lượt** ba nhóm dưới đây, tránh các benchmark đồng thời làm sai lệch phép đo. Các lệnh có thể mất nhiều thời gian vì mỗi trường hợp được chạy năm lần và có giới hạn 100 giây cho mỗi lượt.

### Nhóm A: so sánh năm encoding SAT

```powershell
python.exe playground.py --methods Sequential Binomial Binary Commander Product --sizes 4 8 16 32 64 128 256 512 --timeout 100 --threads 12 --repeats 5 --output results/<ten_file.csv>
```

Số dòng dự kiến: 5 phương pháp × 8 kích thước × 5 lần = **200 dòng dữ liệu**.

### Nhóm B: so sánh bốn solver CP/ILP

```powershell
python.exe playground.py --methods CP-SAT CPLEX-CP CPLEX-MIP Gurobi-MIP --sizes 4 8 16 32 64 128 256 512 --timeout 100 --threads 12 --repeats 5 --output results/<ten_file.csv>
```

Số dòng dự kiến: 4 × 8 × 5 = **160 dòng dữ liệu**. Dùng kết quả nhóm A và B trên các N chung để so sánh SAT với CP/ILP, với cùng thiết lập máy và thời gian.

### Nhóm C: so sánh cả chín phương pháp trên bàn cờ nhỏ

```powershell
python.exe playground.py --methods Sequential Binomial Binary Commander Product CP-SAT CPLEX-CP CPLEX-MIP Gurobi-MIP --sizes 4 6 8 10 12 14 16 --timeout 100 --threads 12 --repeats 5 --output results/<ten_file.csv>
```

Số dòng dự kiến: 9 × 7 × 5 = **315 dòng dữ liệu**.

Các lệnh trên **ghi đè** CSV và metadata cùng tên. Đổi `--output` nếu cần giữ số liệu cũ.

### Tham số

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `--methods` | Tên phương pháp, phân biệt hoa thường | Cả chín phương pháp |
| `--sizes` | Các kích thước N nguyên dương | 4 8 16 32 64 128 256 512 |
| `--timeout` | Giới hạn thời gian mỗi tiến trình, giây | 60 |
| `--threads` | Số luồng cho solver đối chứng; Glucose3 dùng một luồng | 1 |
| `--repeats` | Số lượt chạy mỗi cặp N/phương pháp | 1 |
| `--output` | Đường dẫn CSV | `results/benchmark.csv` |

## 5. Đọc và kiểm tra số liệu

Mỗi CSV có một file `.metadata.json` cùng tên chứa Python, hệ điều hành, CPU được báo bởi Python, phiên bản gói, kích thước, phương pháp, số lần lặp và cấu hình thời gian/luồng.

| Cột | Ý nghĩa |
|---|---|
| `N`, `Method`, `Repeat` | Kích thước, phương pháp và số thứ tự lần chạy |
| `status` | Kết luận của lượt chạy |
| `wall_time` | Thời gian ngoài tiến trình, gồm khởi động, import và thu dọn |
| `build_time` | Thời gian tạo mô hình và khởi tạo bộ giải |
| `solve_time` | Thời gian giải; với solver đối chứng còn gồm đọc nghiệm và một phần thu dọn |
| `total_time` | Tổng thời gian nội bộ sau import, gồm tạo mô hình và giải |
| `variables` | Số biến của mô hình; SAT gồm biến bàn cờ và biến phụ |
| `clauses` | Số clause CNF, dành cho SAT |
| `constraints` | Số ràng buộc mô hình CP/ILP, không tương đương clause SAT |
| `valid` | Kết quả kiểm tra nghiệm; trống khi không có nghiệm để kiểm tra |
| `detail` | Trạng thái gốc hoặc thông báo lỗi |

| Trạng thái | Cách hiểu |
|---|---|
| `SAT` | Tìm được nghiệm và đã kiểm tra nghiệm |
| `UNSAT` | Bộ giải kết luận không có nghiệm |
| `TIMEOUT` | Hết giới hạn thời gian |
| `UNKNOWN` | Bộ giải chưa kết luận, có thể do giới hạn nội tại |
| `UNAVAILABLE` | Thiếu module hoặc executable |
| `ERROR` | Lỗi runtime, giấy phép, mô hình hoặc nghiệm không hợp lệ |

Timeout ngoài áp dụng cho cả khởi động tiến trình, import, tạo mô hình và giải; timeout nội tại của solver đối chứng áp dụng cho bước solve. Vì vậy `wall_time` có thể nhỉnh hơn giới hạn do thu dọn. Các cột đo nội bộ có thể trống nếu bị ngắt. Không coi `TIMEOUT` hoặc `UNKNOWN` là `UNSAT`.
