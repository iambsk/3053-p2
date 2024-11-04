import time
import select
import socket
import traceback
import threading
from frame import Frame

BUFFER_SIZE = 1024

class Hub:
    def __init__(self, port: int = 8000):
        self.port = port
        # Dictionary to store frame buffers for each client
        self.frame_buffers = {}
        # switch table is a dictionary that maps the destination port to the address and socket
        self.switch_table: dict[int, tuple[any, socket.socket]] = {}
        self.lock = threading.RLock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(5)
        print(f"Switch listening on port {self.port}")
        self.accept_connections()
        
    def accept_connections(self):
        while True:
            try:
                # addr is a tuple of (address, port)
                client_socket, addr = self.server_socket.accept()
                self.switch_table[addr[1]] = (addr[0], client_socket)
                # Initialize buffer for new client
                self.frame_buffers[addr[1]] = b''
                print(f"Connection from {addr}")
                threading.Thread(target=self.handle_node, args=(client_socket, addr)).start()
            except socket.error:
                break
    def handle_node(self, client_socket, addr):
        print(f"Node connected from {addr}. Starting communication.")
        # Handle node communication
        while True:
            try:
                frame_bytes = client_socket.recv(BUFFER_SIZE)
                if not frame_bytes:
                    print(f"Connection closed by Node {addr}.")
                    # clean up the buffer since they disconnected
                    with self.lock:
                        if addr[1] in self.frame_buffers:
                            del self.frame_buffers[addr[1]]
                    break
                
                # add all the new frames to the buffer
                with self.lock:
                    # add to the frame buffer for a specific address
                    self.frame_buffers[addr[1]] += frame_bytes
                    buffer = self.frame_buffers[addr[1]]
                    while Frame.DELIMITER.encode() in buffer:
                        # Split the buffer at the first delimiter
                        # frame_data is the first frame
                        # remaining is the rest of the buffer
                        frame_data, remaining = buffer.split(Frame.DELIMITER.encode(), 1)
                        if frame_data:  
                            frame = Frame.from_bytes(frame_data)
                            print(f"Received frame from Node {frame.src} to Node {frame.dest}.")
                            if frame.src not in [i[0] for i in self.switch_table.values()]:
                                self.switch_table[frame.src] = (addr, client_socket)
                                print(f"Node {frame.src} added to switch table.")
                            self.forward_frame(frame, addr)
                        buffer = remaining
                    self.frame_buffers[addr[1]] = buffer

            except Exception as e:
                print(f"Error in handle_node: {e}")
                traceback.print_exc()
                # Clean up buffer on error
                with self.lock:
                    if addr[1] in self.frame_buffers:
                        del self.frame_buffers[addr[1]]
                break

    def forward_frame(self, frame, addr):
        print(f"Forwarding frame from Node {frame.src} to Node {frame.dest}")
        with self.lock:
            if frame.is_ack():
                print(f"Received ACK frame from Node {frame.src} to Node {frame.dest}")
                return
            if frame.dest in self.switch_table:
                try:
                    self.switch_table[frame.dest][1].sendall(frame.to_bytes())
                    print(f"Successfully forwarded frame to Node {frame.dest}")
                except (ConnectionResetError, BrokenPipeError) as e:
                    print(f"Error forwarding to Node {frame.dest}: {e}")
                    del self.switch_table[frame.dest]  # remove if disconnected
                    print(f"Node {frame.dest} removed from switch table due to disconnection.")
            else:
                # broadcast the frame to all other nodes except the sender
                print(f"Broadcasting frame from Node {frame.src} to all other nodes except Node {addr[1]}")
                for port, (_, sock) in self.switch_table.items():
                    if port != addr[1]: 
                        try:
                            sock.sendall(frame.to_bytes())
                            print(f"Broadcasted frame to Node {port}")
                        except (ConnectionResetError, BrokenPipeError) as e:
                            print(f"Broadcast error from Node {frame.src}: {e}")
                            del self.switch_table[port]  # remove disconnected node
                            print(f"Node {port} removed from switch table due to disconnection.")