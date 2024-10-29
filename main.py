import time
import select
import socket
import threading

BUFFER_SIZE = 1024

class Frame:
    def __init__(self, src, dst, size_ack, data=b'', priority=0):
        self.src = src
        self.dst = dst
        self.size_ack = size_ack
        self.data = data
        self.priority = priority

    def to_bytes(self):
        return bytes([self.src, self.dst, self.size_ack, self.priority]) + self.data

    @staticmethod
    def from_bytes(data):
        src = data[0]
        dst = data[1]
        size_ack = data[2]
        priority = data[3]
        frame_data = data[4:]
        return Frame(src, dst, size_ack, frame_data, priority)

class Hub:
    def __init__(self, port: int = 8000):
        self.port = port
        self.frame_buffer: list[Frame] = []
        # switch table is a dictionary that maps the destination port to the address and socket
        self.switch_table: dict[int, tuple[any, socket.socket]] = {}
        self.lock = threading.Lock()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', self.port))
            server_socket.listen(5)
            print(f"Switch listening on port {self.port}")
            while True:
                # addr is a tuple of (address, port)
                client_socket, addr = server_socket.accept()
                if addr not in [i[0] for i in self.switch_table.values()]:
                    self.switch_table[addr[1]] = (addr[0], client_socket)
                print(f"Connection from {addr}")
                threading.Thread(target=self.handle_node, args=(client_socket, addr,)).start()

    def handle_node(self, client_socket, addr):
        # Handle node communication
        with client_socket:
            while True:
                frame_bytes = client_socket.recv(BUFFER_SIZE)
                if not frame_bytes:
                    break
                frame = Frame.from_bytes(frame_bytes)
                with self.lock:
                    if frame.src not in self.switching_table:
                        self.switching_table[frame.src] = client_socket
                    self.forward_frame(frame, addr)
    
    def forward_frame(self, frame: Frame, addr):
        with self.lock:
            if frame.dst in self.switch_table:
                self.switch_table[frame.dst][1].sendall(frame.to_bytes())
            else:
                # broadcast the frame to all other nodes except the sender
                for i in self.switch_table:
                    if i != addr[1]:
                        self.switch_table[i][1].sendall(frame.to_bytes())
            
    def add_frame_to_buffer(self, frame: Frame):
        with self.lock:
            for i in range(len(self.frame_buffer)):
                if self.frame_buffer[i].priority > frame.priority:
                    self.frame_buffer.insert(i, frame)
                    return
            self.frame_buffer.append(frame)
    
    def get_frame_from_buffer(self):
        with self.lock:
            return self.frame_buffer.pop(0)
    
    

