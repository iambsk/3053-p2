class Frame:
    DELIMITER = "|"

    def __init__(self, src, dest, ack=False, data=""):
        self.src = src
        self.dest = dest
        self.ack = ack
        self.data = data
    
    def is_ack(self):
        return self.ack

    def to_bytes(self):
        """Convert frame fields to bytes for transmission."""
        frame = f"{self.src},{self.dest},{int(self.ack)},{self.data}{self.DELIMITER}"
        return frame.encode()

    @classmethod
    def from_bytes(cls, frame_data):
        """Create a Frame object from bytes received over the network."""
        frame_str = frame_data.decode()
        src, dest, ack, data = frame_str.split(",", 3)
        ack = bool(int(ack))
        data = data.rstrip(cls.DELIMITER)  # Remove the trailing delimiter
        return cls(int(src), int(dest), ack, data)
