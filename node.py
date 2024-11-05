import socket
import threading
from frame import Frame

class Node:
    def __init__(self, node_id, switch_host, switch_port):
        self.node_id = node_id
        self.switch_host = switch_host
        self.switch_port = switch_port
        self.input_file = f"node{node_id}.txt"
        self.output_file = f"node{node_id}_output.txt"
        self.socket = None
        self.lock = threading.Lock()

    def connect_to_switch(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.switch_host, self.switch_port))
            print(f"Node {self.node_id} connected to switch.")
        except Exception as e:
            print(f"Error connecting to switch: {e}")

    def send_data(self, dest_id, data, priority=0):
        frame = Frame(src=self.node_id, dest=dest_id, data=data, priority=priority)
        with self.lock:
            # if frame.is_ack():
                # Ignore ACK frames if they are not needed
                # return
            self.socket.sendall(frame.to_bytes())
            print(f"Node {self.node_id} sent data to Node {dest_id} with priority {priority}: {data}")
    
    def receive_data(self):
        buffer = ""
        while True:
            try:
                frame_data = self.socket.recv(1024)
                if not frame_data:
                    print(f"Node {self.node_id} connection closed.")
                    break
                buffer += frame_data.decode()
                while Frame.DELIMITER in buffer:
                    # Split buffer to process each frame
                    frame_str, buffer = buffer.split(Frame.DELIMITER, 1)
                    frame = Frame.from_bytes(frame_str.encode())
                    if frame.dest == self.node_id:
                        if frame.is_ack():
                            print(f"Node {self.node_id} received ACK from Node {frame.src}")
                        else:
                            self.write_output(frame.src, frame.data, frame.priority)
                            # Send ACK back to source
                            ack_frame = Frame(src=self.node_id, dest=frame.src, ack=True)
                            self.socket.sendall(ack_frame.to_bytes())
            except Exception as e:
                print(f"Error receiving data for Node {self.node_id}: {e}")
                break

    def read_input_and_send(self):
        with open(self.input_file, 'r') as file:
            for line in file:
                dest_id, data = line.strip().split(': ')
                # Extract priority from data if present
                if '//' in data:
                    message, priority = data.split('//')
                    priority = int(priority.strip())
                    self.send_data(int(dest_id), message.strip(), priority)
                else:
                    self.send_data(int(dest_id), data.strip())

    def write_output(self, src_id, data, priority=0):
        with open(self.output_file, 'a') as file:
            file.write(f"{src_id}: {data} /// {priority}\n")
        print(f"Node {self.node_id} received data from Node {src_id} with priority {priority}: {data}")
