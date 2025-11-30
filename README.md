# D'Maris Buffet Restaurant - Queue System Simulation

**Môn học:** [CO3007] - Mô hình hóa và Mô phỏng
**Dự án:** Mô phỏng luồng khách hàng và hiệu suất phục vụ tại nhà hàng Buffet D'Maris.

## 1. Giới thiệu (Introduction)

Dự án này mô phỏng hệ thống hàng đợi phức tạp (Network Queueing System) của nhà hàng Buffet D'Maris. [cite_start]Hệ thống được mô hình hóa dưới dạng một mạng lưới các trạm phục vụ (Service Nodes) với luồng khách hàng ngẫu nhiên di chuyển giữa các quầy thức ăn khác nhau[cite: 1, 17].

Mục tiêu của dự án là phân tích hiệu suất hệ thống, xác định điểm nghẽn (bottleneck) và tối ưu hóa quy trình phục vụ dựa trên các thông số thực tế.

## 2. Kiến trúc Hệ thống (System Architecture)

[cite_start]Hệ thống bao gồm các thành phần chính sau[cite: 21]:

* **Nguồn (Sources):** 2 lối vào riêng biệt (Entrance A & B).
* **Thanh toán (Payment Stations):** 2 quầy thu ngân hoạt động độc lập.
* **Khu vực phục vụ (Service Stations):** 4 quầy thức ăn chính (Salad, Món chính, Tráng miệng, Đồ uống).
* **Đích (Sink):** Khu vực bàn ăn (khách rời khỏi hệ thống hàng đợi).

### Sơ đồ luồng (Flow Overview)
`Entrance -> Payment -> Food Stations (Random Routing) -> Sink`

## 3. Thông số Kỹ thuật (Technical Specifications)

Dữ liệu đầu vào và cấu hình các trạm phục vụ được định nghĩa như sau:

### A. Nguồn khách (Arrival Process)
[cite_start]Phân phối Poisson (Markovian)[cite: 26, 32].

| Node | Tên | Arrival Rate ($\lambda$) | Đi đến |
| :--- | :--- | :--- | :--- |
| Node 1 | Entrance A | 2.0 khách/phút | Payment Counter A (100%) |
| Node 2 | Entrance B | 1.0 khách/phút | Payment Counter B (100%) |

### B. Các trạm phục vụ (Service Nodes)
[cite_start]Thời gian phục vụ tuân theo phân phối Mũ (Exponential)[cite: 42, 61].

| Node ID | Tên Trạm | Mô hình (Kendall) | Server ($m$) | Service Rate ($\mu$) | Capacity ($K$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Node 3** | Payment A | M/M/1/10 | 1 | 3.0 /phút | 10 |
| **Node 4** | Payment B | M/M/1/10 | 1 | 3.0 /phút | 10 |
| **Node 5** | Salad Bar | M/M/3 | 3 | 0.5 /phút | $\infty$ |
| **Node 6** | Main Course| M/M/5 | 5 | 0.25 /phút | $\infty$ |
| **Node 7** | Dessert | M/M/2 | 2 | 1.0 /phút | $\infty$ |
| **Node 8** | Drink | M/M/4 | 4 | 2.0 /phút | $\infty$ |

[cite_start]*(Ghi chú: Node 3 và 4 có hàng đợi hữu hạn K=10, các node khác có hàng đợi vô hạn)*[cite: 41, 49].

## 4. Logic Định tuyến (Routing Logic)

[cite_start]Khách hàng di chuyển giữa các trạm dựa trên ma trận xác suất sau[cite: 82]:

**Từ Quầy Thanh toán (PC-A & PC-B):**
* 40% $\rightarrow$ Salad Bar
* 50% $\rightarrow$ Main Course
* 10% $\rightarrow$ Drink Station

**Từ Salad Bar:**
* 80% $\rightarrow$ Main Course
* 10% $\rightarrow$ Drink Station
* 10% $\rightarrow$ Sink (Ra bàn ăn)

**Từ Main Course:**
* 60% $\rightarrow$ Dessert Station
* 20% $\rightarrow$ Drink Station
* 10% $\rightarrow$ Main Course (Lấy thêm)
* 10% $\rightarrow$ Sink

**Từ Dessert Station:**
* 40% $\rightarrow$ Drink Station
* 10% $\rightarrow$ Main Course
* 50% $\rightarrow$ Sink

**Từ Drink Station:**
* 40% $\rightarrow$ Main Course
* 30% $\rightarrow$ Dessert Station
* 10% $\rightarrow$ Salad Bar
* 20% $\rightarrow$ Sink
