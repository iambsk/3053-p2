import time
import select
import socket
import threading
from frame import Frame

BUFFER_SIZE = 1024

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
				try:
					# addr is a tuple of (address, port)
					client_socket, addr = server_socket.accept()
					self.switch_table[addr[1]] = (addr[0], client_socket)
					print(f"Connection from {addr}")
					threading.Thread(target=self.handle_node, args=(client_socket, addr)).start()
				except socket.error:
					break

	def handle_node(self, client_socket, addr):
		# Handle node communication
		with client_socket:
			while True:
				try:
					frame_bytes = client_socket.recv(BUFFER_SIZE)
					if not frame_bytes:
						break
					frame = Frame.from_bytes(frame_bytes)
					with self.lock:
						if frame.src not in self.switch_table:
							self.switch_table[frame.src] = client_socket
						self.forward_frame(frame, addr)
				except Exception as e:
					print(f"Error in handle_node: {e}")
					break

	def forward_frame(self, frame, addr):
		with self.lock:
			if frame.dest in self.switch_table:
				try:
					self.switch_table[frame.dest][1].sendall(frame.to_bytes())
				except (ConnectionResetError, BrokenPipeError) as e:
					print(f"Error forwarding to Node {frame.dest}: {e}")
					del self.switch_table[frame.dest]  # Remove if disconnected
			else:
				# broadcast the frame to all other nodes except the sender
				for port, (_, sock) in self.switch_table.items():
					if port != addr[1]: 
						try:
							sock.sendall(frame.to_bytes())
						except (ConnectionResetError, BrokenPipeError) as e:
							print(f"Broadcast error from Node {frame.src}: {e}")
							del self.switch_table[port]  # Remove disconnected node
