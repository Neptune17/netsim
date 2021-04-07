import os

from objects.simluator import Simluator

from solution.sender.cc_solution.reno import Reno
from solution.sender.block_scheduler_solution.fifo import FIFO
from solution.router.queue_scheduler_solution.sp import SP

from config.constant import *

if __name__ == '__main__':

    net_trace1 = "dataset/link_trace/trace1.txt"
    net_trace2 = "dataset/link_trace/trace1.txt"
    net_trace3 = "dataset/link_trace/trace1.txt"
    net_trace4 = "dataset/link_trace/trace1.txt"

    block_trace1 = "dataset/block_trace/GTA.txt"

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC", "192.168.0.1", FIFO(), Reno()), 
            (objectType.SENDER, "DEST", "192.168.1.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router", ["192.168.0.2", "192.168.1.2"], [2000, 2000], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2"}, SP(), 6.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", net_trace1),
            ("192.168.1.2", "192.168.1.1", net_trace2),
            ("192.168.1.1", "192.168.1.2", net_trace3),
            ("192.168.0.2", "192.168.0.1", net_trace4)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.1.1", block_trace1)
        ]
    }

    def del_all(path):
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path, i)
            if os.path.isdir(c_path):
                del_all(c_path)
                os.rmdir(c_path)
            else:
                os.remove(c_path)    

    if os.path.exists("output/"):
        del_all("output")
    
    os.makedirs("output/packet_log")
    os.mknod("output/packet_log/packet-0.log")

    testsimluator = Simluator(config_dict, "output/")
    testsimluator.run()