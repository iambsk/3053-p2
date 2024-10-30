class Frame:
    def __init__(self, src, dest, size_ack=None, data=""):
        self.src = src
        self.dest = dest
        self.size_ack = len(data) if data else size_ack
        self.data = data

    def to_bytes(self):
        """Convert frame fields to bytes for transmission."""
        frame = bytearray()
        frame.append(self.src)               # 1 byte for SRC
        frame.append(self.dest)              # 1 byte for DEST
        frame.append(self.size_ack)          # 1 byte for SIZE/ACK
        frame.extend(self.data.encode())     # Remaining bytes for data
        return bytes(frame)

    @classmethod
    def from_bytes(cls, frame_data):
        """Create a Frame object from bytes received over the network."""
        src = frame_data[0]
        dest = frame_data[1]
        size_ack = frame_data[2]
        data = frame_data[3:].decode() if size_ack != 0 else ""
        return cls(src, dest, size_ack, data)
