class Frame:
    DELIMITER = "|"

    def __init__(self, src, dest, ack=False, data="", priority=False):
        self.src = src
        self.dest = dest
        self.ack = ack
        self.data = data
        self.priority = priority  # New attribute for frame priority

    def to_bytes(self):
        frame = f"{self.src},{self.dest},{int(self.ack)},{self.data},{int(self.priority)}{self.DELIMITER}"
        return frame.encode()
    
    def is_ack(self):
        return self.ack

    @classmethod
    def from_bytes(cls, frame_data):
        frame_str = frame_data.decode()
        src, dest, ack, data, priority = frame_str.split(",", 4)
        print(f"Frame details:")
        print(f"  Source: Node {src}")
        print(f"  Destination: Node {dest}")
        print(f"  Priority: {priority}")
        print(f"  Data: {data}")
        ack = bool(int(ack))
        priority = bool(int(priority.rstrip(cls.DELIMITER)))
        return cls(int(src), int(dest), ack, data, priority)