from netmiko import ConnectHandler

# Định nghĩa các router
R1 = {
    "device_type": "mikrotik_routeros",
    "ip": "192.168.109.10",
    "username": "admin",
    "password": "123",
}
R2 = {
    "device_type": "mikrotik_routeros",
    "ip": "192.168.109.20",
    "username": "admin",
    "password": "123",
}
R3 = {
    "device_type": "mikrotik_routeros",
    "ip": "192.168.109.30",
    "username": "admin",
    "password": "123",
}
list_router = [R1, R2, R3]

# Hiển thị menu cho người dùng
def menu():
    print("1. Show tất cả các router")
    print("2. Show địa chỉ IP của từng router")
    print("3. Kiểm tra kết nối mạng với các router")
    print("4. Thêm/Xóa địa chỉ IP vào router")
    print("5. Thêm/Xóa địa chỉ DHCP vào router")
    print("6. Thoát chương trình")
    print("7. cap nhat router")
    return int(input("Chọn một tùy chọn (1-6): "))

# Hiển thị thông tin tất cả các router
def show_all_routers():
    for router in list_router:
        net_connect = ConnectHandler(**router)
        name = net_connect.send_command("/system identity print")
        print(f"Router: {router['ip']}")
        print(f"Tên router: {name}")
        print("-------------")

# Hiển thị địa chỉ IP của từng router
def show_ip_addresses():
    for router in list_router:
        net_connect = ConnectHandler(**router)
        output = net_connect.send_command("/ip address print")
        print(f"Địa chỉ IP của router {router['ip']}:")
        print(output)
        print("-------------")

# Kiểm tra kết nối mạng với các router
def check_network_connection():
    for router in list_router:
        try:
            net_connect = ConnectHandler(**router)
            print(f"Kết nối thành công với router {router['ip']}")
        except Exception as e:
            print(f"Không thể kết nối với router {router['ip']}: {e}")

# Cấu hình DHCP trên router
def add_dhcp():
    print("Danh sách các router:")
    for i, router in enumerate(list_router):
        print(f"{i + 1}. Router {router['ip']}")
    
    try:
        choice = int(input("Chọn router bạn muốn cấu hình DHCP (1-3): ")) - 1
        if choice not in range(len(list_router)):
            print("Chọn không hợp lệ. Vui lòng thử lại.")
            return
    except ValueError:
        print("Lựa chọn không hợp lệ.")
        return

    net_connect = ConnectHandler(**list_router[choice])
    action = input("Bạn muốn thêm hay xóa DHCP (add/remove): ").strip().lower()

    if action == "add":
        print("Nhập thông tin địa chỉ máy chủ DHCP:")
        address = input("Nhập Địa chỉ mạng (ví dụ: 192.168.109.0/24): ")
        interface1 = input("Nhập tên interface (VD: ether1): ")
        gateway = input("Nhập Địa chỉ Gateway (ví dụ: 192.168.109.1): ")
        dns = input("Nhập Địa chỉ DNS (ví dụ: 8.8.8.8, 8.8.4.4): ")

        print("Nhập dải địa chỉ IP mà DHCP sẽ cấp phát:")
        ranges_start = input("Nhập địa chỉ IP đầu (ví dụ: 192.168.109.100): ")
        ranges_end = input("Nhập địa chỉ IP cuối (ví dụ: 192.168.109.200): ")

        # Kiểm tra nếu đã có DHCP server
        check_dhcp = net_connect.send_command("/ip dhcp-server print")
        if "disabled" not in check_dhcp:  # Kiểm tra xem đã có DHCP server
            print("Đã có DHCP server. Xóa DHCP cũ trước khi thêm mới.")
            net_connect.send_command("/ip dhcp-server remove [find]")  # Xóa DHCP cũ

        # Cấu hình các lệnh DHCP
        commands = [
            f"/ip address add address={address} interface={interface1}",
            f"/ip firewall nat add chain=srcnat action=masquerade out-interface={interface1}",
            f"/ip pool add name=dhcp_pool1 ranges={ranges_start}-{ranges_end}",
            f"/ip dhcp-server add name=dhcp1 interface={interface1} address-pool=dhcp_pool1 disabled=no",
            f"/ip dhcp-server network add address={address} gateway={gateway} dns-server={dns}",
        ]

        # Gửi các lệnh
        for command in commands:
            net_connect.send_command(command)

        print(f"Đã thêm DHCP vào router {list_router[choice]['ip']}")
    
    elif action == "remove":
        print("Xóa DHCP server và pool...")
        # Xóa DHCP server và pool
        print("Danh sách các địa chỉ IP hiện có trên router:")
        ip_addresses = net_connect.send_command("/ip address print")
        print(ip_addresses)
        value1 = input("Nhập số dòng muốn xóa:")
        value1 = int(value1)
        command = f"/ip address remove numbers={value1}"
        net_connect.send_command(command)
        print(f"Đã xóa DHCP khỏi router {list_router[choice]['ip']}")

        # Hiển thị các DHCP server hiện có trên router
        print("Danh sách các DHCP server hiện có trên router:")
        dhcp_servers = net_connect.send_command("/ip dhcp-server print")
        print(dhcp_servers)

        # Nhập số dòng muốn xóa
        value2 = input("Nhập số dòng muốn xóa: ")
        value2 = int(value2)  # Ép kiểu thành số nguyên

        # Lệnh xóa DHCP server dựa trên số dòng đã nhập
        command = f"/ip dhcp-server remove numbers={value2}"
        net_connect.send_command(command)
        print(f"Đã xóa DHCP server tại dòng {value2} khỏi router {list_router[choice]['ip']}")

        # Hiển thị các DHCP pool hiện có trên router
        print("Danh sách các DHCP pool hiện có trên router:")
        dhcp_pools = net_connect.send_command("/ip pool print")
        print(dhcp_pools)

        # Nhập số dòng muốn xóa
        value3 = input("Nhập số dòng muốn xóa: ")
        value3 = int(value3)  # Ép kiểu thành số nguyên

        # Lệnh xóa DHCP pool dựa trên số dòng đã nhập
        command = f"/ip pool remove numbers={value3}"
        net_connect.send_command(command)
        
        print(f"Đã xóa DHCP pool tại dòng {value3} khỏi router {list_router[choice]['ip']}")

        # Hiển thị các DHCP networks hiện có trên router
        print("Danh sách các DHCP networks hiện có trên router:")
        dhcp_networks = net_connect.send_command("/ip dhcp-server network print")
        print(dhcp_networks)

        # Nhập số dòng muốn xóa
        value4 = input("Nhập số dòng muốn xóa DHCP network: ")
        value4 = int(value4)  # Ép kiểu thành số nguyên

        # Lệnh xóa DHCP network dựa trên số dòng đã nhập
        command = f"/ip dhcp-server network remove numbers={value4}"
        net_connect.send_command(command)
        print(f"Đã xóa DHCP network tại dòng {value4} khỏi router {list_router[choice]['ip']}")

    else:
        print("Lệnh không hợp lệ, vui lòng chọn 'add' hoặc 'remove'.")

# Thêm hoặc xóa địa chỉ IP trên router
def modify_ip_address():
    print("Danh sách các router:")
    for i, router in enumerate(list_router):
        print(f"{i + 1}. Router {router['ip']}")
    
    try:
        choice = int(input("Chọn router bạn muốn thay đổi địa chỉ IP (1-3): ")) - 1
        if choice not in range(len(list_router)):
            print("Chọn không hợp lệ. Vui lòng thử lại.")
            return
    except ValueError:
        print("Lựa chọn không hợp lệ.")
        return

    net_connect = ConnectHandler(**list_router[choice])
    action = input("Bạn muốn thêm hay xóa địa chỉ IP (add/remove): ").strip().lower()
    
    if action == "add":
        ip_address = input("Nhập địa chỉ IP muốn thêm (VD: 192.168.109.10/24): ")
        interface = input("Nhập tên interface (VD: ether1): ")
        command = f"/ip address add address={ip_address} interface={interface}"
        net_connect.send_command(command)
        print(f"Đã thêm địa chỉ IP {ip_address} vào router {list_router[choice]['ip']}")
    
    elif action == "remove":
        print("Danh sách các địa chỉ IP hiện có trên router:")
        ip_addresses = net_connect.send_command("/ip address print")
        print(ip_addresses)
        value1 = input("Nhập số dòng muốn xóa:")
        value1 = int(value1)
        command = f"/ip address remove numbers={value1}"
        net_connect.send_command(command)
        print(f"Đã xóa DHCP khỏi router {list_router[choice]['ip']}")
    
    else:
        print("Lệnh không hợp lệ, vui lòng chọn 'add' hoặc 'remove'.")

# Chương trình chính
while True:
    option = menu()
    if option == 1:
        show_all_routers()
    elif option == 2:
        show_ip_addresses()
    elif option == 3:
        check_network_connection()
    elif option == 4:
        modify_ip_address()
    elif option == 5:
        add_dhcp()
    elif option == 6:
        break
    else:
        print("Tùy chọn không hợp lệ, hãy thử lại.")
    
    cont = input("Bạn có muốn tiếp tục không? (y/n): ").strip().lower()
    if cont != 'y':
        break
