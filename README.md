# 3053-p2
Members:
- Brian Kessel
- Max Strack
- Ben Mannal

## How to run
```bash
python3 nodeGen.py <number of nodes>
python3 main.py <number of nodes>
```

## Files
main.py: Runs the program.
nodeGen.py: Generates the input and output files for the nodes.
node.py: The node class, which contains the logic for the nodes.
hub.py: The switch class, which contains the logic for the switch.
frame.py: The frame class, which contains the logic for the frames.

## Frame Specification

```python
class Frame:
    DELIMITER = "|"

    def __init__(self, src, dest, ack=False, data=""):
        self.src = src
        self.dest = dest
        self.ack = ack
        self.data = data
```

The frame is designed like so: "src,dest,ack,data,delimiter".
There is no limit on the data size, other than the buffer size of the socket.



## Checklist

| Feature | Status/Description |
|---------|-------------------|
| Project Compiles and Builds without warnings or errors | Complete |
| Switch class | Complete |
| Switch has a frame buffer, and reads/writes appropriately | Complete |
| Switch allows multiple connections | Complete |
| Switch floods frame when it doesn't know the destination | Complete |
| Switch learns destinations, and doesn't forward packet to any port except the one required | Complete |
| Switch acts like a hub | Complete |
| Node class | Complete |
| Nodes instantiate, and open connection to the switch | Complete |
| Nodes open their input files, and send data to switch | Complete |
| Nodes open their output files, and save data that they received | Complete |

## Extra Credit

Backbone Switching: https://github.com/iambsk/3053-p2/tree/backbone
Star Switching: https://github.com/iambsk/3053-p2/tree/star
Frame priority: https://github.com/iambsk/3053-p2/tree/frame-priority

## Bugs

None
