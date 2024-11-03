import time
import select
import socket
import traceback
import threading
from hub import Hub
from frame import Frame

BUFFER_SIZE = 1024

class BackboneHub(Hub):
    def __init__(self, port: int = 8001):
        self.port = port
        self.frame_buffer: list[Frame] = []
        # switch table is a dictionary that maps the destination port to the address and socket
        self.switch_table: dict[int, tuple[any, socket.socket]] = {}
        self.lock = threading.Lock()
        self.backbone_socket = None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', self.port))
            server_socket.listen(5)
            print(f"Switch listening on port {self.port}")
            while True:
                try:
                    # addr is a tuple of (address, port)
                    client_socket, addr = server_socket.accept()
                    self.switch_table[addr[1]] = (addr[0], client_socket)
                    print(f"Connection from {addr}")
                    threading.Thread(target=self.handle_node, args=(client_socket, addr)).start()
                except socket.error:
                    break
        self.switches = []  # the switches connected

    def accept_connections(self):
        while True:
            switch_socket, _ = self.server_socket.accept()
            self.switches.append(switch_socket)
            threading.Thread(target=self.handle_switch, args=(switch_socket,)).start()

    def handle_switch(self, switch_socket):
        while True:
            frame_bytes = switch_socket.recv(BUFFER_SIZE)
            if not frame_bytes:
                break
            frame = Frame.from_bytes(frame_bytes)
            for socket in self.switches:
                if socket != switch_socket:
                    socket.sendall(frame.to_bytes())
