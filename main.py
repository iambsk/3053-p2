import sys
import threading
import time
from hub import Hub
from node import Node

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_nodes>")
        return

    num_nodes = int(sys.argv[1])
    if not (2 <= num_nodes <= 255):
        print("Number of nodes should be between 2 and 255.")
        return

    hub_port = 8000
    hub_thread = threading.Thread(target=Hub, args=(hub_port,))
    hub_thread.start()

    time.sleep(1)

    # Connect each node
    nodes = []
    node_threads = []
    for node_id in range(1, num_nodes + 1):
        node = Node(node_id, 'localhost', hub_port)
        node.connect_to_switch()
        node_thread = threading.Thread(target=node.receive_data)
        node_thread.start()
        node_threads.append(node_thread)
        nodes.append(node)

    # Start transmission
    send_threads = []
    for node in nodes:
        send_thread = threading.Thread(target=node.read_input_and_send)
        send_thread.start()
        send_threads.append(send_thread)

    # Wait for all send threads to finish before joining receive threads
    for send_thread in send_threads:
        send_thread.join()

    # close all node_threads
    for node_thread in node_threads:
        node_thread.join()

    print("All nodes have finished sending data.")

if __name__ == "__main__":
    main()