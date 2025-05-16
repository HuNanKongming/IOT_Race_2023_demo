import socket
import mysql.connector
import json
import threading
import time
import datetime

# 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "sensor_data"
}
# 保存所有客户端连接
client_sockets = []
# 插入数据到数据库
def insert_to_database(temperature, humidity, light):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO sensor_table (temperature, humidity, light) VALUES (%s, %s, %s)"
        cursor.execute(query, (temperature, humidity, light))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# 处理客户端连接
def handle_client(client_socket, client_address):
    global client_sockets
    client_sockets.append(client_socket)
    print(f"Connection from {client_address}")
    # 发送连接成功后的时间数据，延迟 2 秒
    time.sleep(2)  # 延迟 2 秒
    now = datetime.datetime.now()
    date_time = f"SF{now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}E"
    try:
        client_socket.send(date_time.encode("utf-8"))
        print(f"Sent to {client_address}: {date_time}")
    except Exception as e:
        print(f"Failed to send data to {client_address}: {e}")

    while True:
        try:
            # 接收数据
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                print(f"Client {client_address} disconnected")
                break
            print(f"Received data: {data}")
            # 检查数据格式是否为 "S*****E"
            if data.startswith("S") and len(data) > 1 and data[-2] == "E":
                # 广播 "S*****E" 格式数据
                broadcast_data(data[0:-1])
                print(f"Broadcasted data: {data[0:-1]}")
            elif data.startswith("#") and len(data) > 1 and data[-3] == "@":
                # 广播 "S*****E" 格式数据
                broadcast_data(data[0:-1])
                print(f"Broadcasted data: {data[0:-1]}")
            else:
                # 假设数据是 JSON 格式
                try:
                    sensor_data = json.loads(data)
                    temperature = sensor_data.get("temperature")
                    humidity = sensor_data.get("humidity")
                    light = sensor_data.get("light")
                    # print(f"Temperature: {temperature}, Humidity: {humidity}, Light: {light}")
                    # 插入数据到数据库
                    insert_to_database(temperature, humidity, light)
                    # 将温度和湿度格式化为"%02d%02d"格式
                    formatted_data = f"[{int(temperature):02d}{int(humidity):02d}{int(light):03d}]"
                    broadcast_data(formatted_data)
                except json.JSONDecodeError:
                    print("Received data is not in JSON format")

        except ConnectionResetError:
            print(f"Connection with {client_address} was forcibly closed")
            break

    # 移除断开的客户端
    client_sockets.remove(client_socket)
    client_socket.close()

# 广播数据给所有已连接的客户端
def broadcast_data(data):
    for client in client_sockets:
        try:
            client.send(data.encode("utf-8"))
            # print(f"Broadcasted data: {data}")
        except:
            client_sockets.remove(client)

# 启动服务器
def start_server(host="192.168.206.254", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
