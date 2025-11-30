import simpy
import numpy as np
import collections

SIM_TIME = 6000 #(phút)

# Tốc độ đến (khách/phút)
LAMBDA_A = 2.0  # Nguồn A
LAMBDA_B = 1.0  # Nguồn B

# Trạm Thanh toán (M/M/1/10)
MU_PCA = 3.0     # Tốc độ phục vụ PC-A
SERVERS_PCA = 1  # Số máy chủ PC-A
K_PCA = 10       # Sức chứa hệ thống PC-A

MU_PCB = 3.0     # Tốc độ phục vụ PC-B
SERVERS_PCB = 1  # Số máy chủ PC-B
K_PCB = 10       # Sức chứa hệ thống PC-B

# Trạm Thức ăn (M/M/c)
MU_SALAD = 0.5     # Tốc độ phục vụ Salad
SERVERS_SALAD = 3  # Số quầy Salad

MU_MAIN = 0.25     # Tốc độ phục vụ Món chính
SERVERS_MAIN = 5   # Số quầy Món chính

MU_DESSERT = 1.0     # Tốc độ phục vụ Tráng miệng
SERVERS_DESSERT = 2  # Số quầy Tráng miệng

MU_DRINK = 2.0     # Tốc độ phục vụ Đồ uống
SERVERS_DRINK = 4  # Số quầy Đồ uống

#Các luồng định tuyến
ROUTING_FROM_PAYMENT = {
    'Salad': 0.40,
    'Main': 0.50,
    'Drink': 0.10
}


ROUTING_FROM_SALAD = {
    'Main': 0.80,
    'Drink': 0.10,
    'Sink': 0.10
}


ROUTING_FROM_MAIN = {
    'Dessert': 0.60,
    'Main': 0.10,
    'Drink': 0.20,
    'Sink': 0.10
}


ROUTING_FROM_DESSERT = {
    'Drink': 0.40,
    'Sink': 0.50,
    'Main': 0.10
}


ROUTING_FROM_DRINK = {
    'Main': 0.40,
    'Dessert': 0.30,
    'Sink': 0.20,
    'Salad': 0.10
}


ROUTING_RULES = {
    'PC-A': ROUTING_FROM_PAYMENT,
    'PC-B': ROUTING_FROM_PAYMENT,
    'Salad': ROUTING_FROM_SALAD,
    'Main': ROUTING_FROM_MAIN,
    'Dessert': ROUTING_FROM_DESSERT,
    'Drink': ROUTING_FROM_DRINK
}


#Class cho các node
class Station:
    def __init__(self, env, name, num_servers, service_rate, capacity=float('inf')):
        self.env = env
        self.name = name

        self.server = simpy.Resource(env, capacity=num_servers)
        self.service_rate = service_rate
        self.capacity = capacity

        self.num_in_system = 0

    def get_service_time(self):
        return np.random.exponential(1.0 / self.service_rate)


def customer_journey(env, name, current_location, stations, stats):
    system_arrival_time = env.now
    while current_location != 'Sink':

        station = stations[current_location]
        node_arrival_time = env.now

        if station.capacity < float('inf'):
            if station.num_in_system >= station.capacity:
                # Hàng đợi đầy, khách hàng bị từ chối (lost)
                stats['lost'][station.name] += 1
                return
            station.num_in_system += 1

        with station.server.request() as req:
            yield req

            wait = env.now - node_arrival_time
            stats['wait_times'][station.name].append(wait)

            service_time = station.get_service_time()
            yield env.timeout(service_time)

        if station.capacity < float('inf'):
            station.num_in_system -= 1

        rules = ROUTING_RULES[current_location]
        destinations = list(rules.keys())
        probabilities = list(rules.values())

        current_location = np.random.choice(destinations, p=probabilities)

    total_system_time = env.now - system_arrival_time
    stats['system_time'].append(total_system_time)
    stats['completed'] += 1


#Tạo nguồn khách
def source_generator(env, name, lambda_rate, entry_point, stations, stats):
    customer_id = 0
    while True:
        iat = np.random.exponential(1.0 / lambda_rate)
        yield env.timeout(iat)

        customer_id += 1
        customer_name = f"{name}-{customer_id}"
        stats['arrivals'][name] += 1

        env.process(customer_journey(env, customer_name, entry_point, stations, stats))


#Simulation
def run_simulation():
    print(f"Bắt đầu mô phỏng Buffet D'Maris (thời gian: {SIM_TIME} phút)")
    env = simpy.Environment()

    stats = {
        'arrivals': collections.defaultdict(int),
        'lost': collections.defaultdict(int),
        'completed': 0,
        'wait_times': collections.defaultdict(list),
        'system_time': []
    }

    # Tạo trạm
    stations = {
        'PC-A': Station(env, 'PC-A', SERVERS_PCA, MU_PCA, K_PCA),
        'PC-B': Station(env, 'PC-B', SERVERS_PCB, MU_PCB, K_PCB),
        'Salad': Station(env, 'Salad', SERVERS_SALAD, MU_SALAD),
        'Main': Station(env, 'Main', SERVERS_MAIN, MU_MAIN),
        'Dessert': Station(env, 'Dessert', SERVERS_DESSERT, MU_DESSERT),
        'Drink': Station(env, 'Drink', SERVERS_DRINK, MU_DRINK)
    }


    env.process(source_generator(env, 'Entrance-A', LAMBDA_A, 'PC-A', stations, stats))
    env.process(source_generator(env, 'Entrance-B', LAMBDA_B, 'PC-B', stations, stats))


    env.run(until=SIM_TIME)

    print("\n--- Kết quả Mô phỏng ---")
    print(f"Tổng số khách hàng đến (A): {stats['arrivals']['Entrance-A']}")
    print(f"Tổng số khách hàng đến (B): {stats['arrivals']['Entrance-B']}")
    total_arrivals = sum(stats['arrivals'].values())
    print(f"TỔNG SỐ KHÁCH HÀNG: {total_arrivals}")

    print("\n--- Khách hàng bị từ chối (Hàng đợi thanh toán đầy) ---")
    lost_a = stats['lost']['PC-A']
    lost_b = stats['lost']['PC-B']
    total_lost = lost_a + lost_b
    print(f"Bị từ chối tại PC-A: {lost_a} ({(lost_a / total_arrivals) * 100:.2f}%)")
    print(f"Bị từ chối tại PC-B: {lost_b} ({(lost_b / total_arrivals) * 100:.2f}%)")
    print(f"TỔNG SỐ BỊ TỪ CHỐI: {total_lost}")

    print(f"\nTổng số khách hoàn thành (đến Sink): {stats['completed']}")

    print("\n--- Thống kê thời gian (phút) ---")
    if stats['system_time']:
        avg_sys_time = np.mean(stats['system_time'])
        print(f"Thời gian trung bình trong hệ thống: {avg_sys_time:.2f} phút")
    else:
        print("Không có khách hàng nào hoàn thành.")

    print("\nThời gian chờ trung bình tại mỗi trạm:")
    for station_name, times in stats['wait_times'].items():
        if times:
            avg_wait = np.mean(times)
            print(f"  - {station_name}: {avg_wait:.2f} phút")
        else:
            print(f"  - {station_name}: 0.00 phút (không có dữ liệu)")


if __name__ == "__main__":
    run_simulation()