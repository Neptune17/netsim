import os
import json
import matplotlib.pyplot as plt

from objects.simluator import Simluator

from solution.sender.cc_solution.reno import Reno
from solution.sender.block_scheduler_solution.fifo import FIFO
from solution.router.queue_scheduler_solution.sp import SP

from config.constant import *

from utils import *
from log_utils import *

if __name__ == '__main__':

    print("single stream test")
    print("--------------------------------------------------------------------------")

    net_trace1 = "dataset/link_trace/trace1.txt"
    net_trace2 = "dataset/link_trace/trace1.txt"
    net_trace3 = "dataset/link_trace/trace1.txt"
    net_trace4 = "dataset/link_trace/trace1.txt"

    block_trace1 = "dataset/block_trace/GTA.txt"

    log_root_dir = "outputsingle/"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC", "192.168.0.1", FIFO(), Reno(log_root_dir + "solution/")), 
            (objectType.SENDER, "DEST", "192.168.1.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router", ["192.168.0.2", "192.168.1.2"], [50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2"}, SP(), 2.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", net_trace1),
            ("192.168.1.1", "192.168.1.2", net_trace3),
            ("192.168.0.2", "192.168.0.1", net_trace4),
            ("192.168.1.2", "192.168.1.1", net_trace2)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.1.1", block_trace1)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    print(json.dumps(packet_statistics(log_root_dir + "packet_log/", "192.168.0.1"), indent=4))
    print(json.dumps(packet_statistics(log_root_dir + "packet_log/", "192.168.1.1"), indent=4))

    print("--------------------------------------------------------------------------")

    tar_interval_time = 0.05
    tar_interval_count = 40

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    plt.title("Src Send")
    plt.xlabel("Time(s)")
    plt.ylabel("Rate(Mbps)")

    for log in src_timeline_data["send"]:
        plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"][log], label = log)
    plt.legend()
    plt.savefig(log_root_dir + "timeline/SrcSend.jpg")
    plt.close()

    plt.title("Src Receive")
    plt.xlabel("Time(s)")
    plt.ylabel("Rate(Mbps)")

    for log in src_timeline_data["receive"]:
        plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["receive"][log], label = log)
    plt.legend()
    plt.savefig(log_root_dir + "timeline/SrcReceive.jpg")
    plt.close()

    print("--------------------------------------------------------------------------")

    tar_interval_time = 0.01
    tar_interval_count = 2000

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    plt.title("Reno Analyze")
    plt.xlabel("Time(s)")
    plt.ylabel("Rate(Mbps)")

    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], label = "src total")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["lost"], label = "src lost")

    router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["total"], label = "router in")
    router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["lost"], label = "router drop")
    router_out_data = timeline(log_root_dir + "packet_log/", "192.168.1.2", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_out_data["send"]["total"], label = "router out")

    f_solution = open(log_root_dir + "solution/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]) / 10)
    plt.plot(x, y, label = "CWND")

    f_router = open(log_root_dir + "router_log/router.log")
    x = []
    y = []
    for line in f_router.readlines():
        data = json.loads(line.replace("'", '"'))
        if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
            continue
        
        x.append(float(data["event_time"]))
        y.append(int(data["192.168.1.2"][1]) / 10)
    plt.plot(x, y, label = "router QUEUE")

    plt.legend()
    plt.savefig(log_root_dir + "timeline/RenoAnalyze.jpg")
    plt.close()

    print("multi stream test")
    print("--------------------------------------------------------------------------")

    net_trace = "dataset/link_trace/trace1.txt"

    block_trace0 = "dataset/block_trace/FULL0.txt"
    block_trace5 = "dataset/block_trace/FULL1.txt"
    block_trace10 = "dataset/block_trace/FULL2.txt"

    log_root_dir = "outputmulti/"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution1/")
    os.makedirs(log_root_dir + "solution2/")
    os.makedirs(log_root_dir + "solution3/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1", "192.168.0.1", FIFO(), Reno(log_root_dir + "solution1/")), 
            (objectType.SENDER, "SRC2", "192.168.1.1", FIFO(), Reno(log_root_dir + "solution2/")), 
            (objectType.SENDER, "SRC3", "192.168.2.1", FIFO(), Reno(log_root_dir + "solution3/")), 
            (objectType.SENDER, "DEST", "192.168.3.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router", ["192.168.0.2", "192.168.1.2", "192.168.2.2", "192.168.3.2"], [50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2", "192.168.2.0/24" : "192.168.2.2", "192.168.3.0/24" : "192.168.3.2"}, SP(), 2.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", net_trace),
            ("192.168.1.1", "192.168.1.2", net_trace),
            ("192.168.2.1", "192.168.2.2", net_trace),
            ("192.168.3.1", "192.168.3.2", net_trace),
            ("192.168.0.2", "192.168.0.1", net_trace),
            ("192.168.1.2", "192.168.1.1", net_trace),
            ("192.168.2.2", "192.168.2.1", net_trace),
            ("192.168.3.2", "192.168.3.1", net_trace)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.3.1", block_trace0),
            ("192.168.1.1", "192.168.3.1", block_trace5),
            ("192.168.2.1", "192.168.3.1", block_trace10)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    print("--------------------------------------------------------------------------")

    tar_interval_time = 0.5
    tar_interval_count = 160

    plt.figure(figsize = (20,6))
    plt.title("Multi Reno Analyze")
    plt.xlabel("Time(s)")
    plt.ylabel("Rate(Mbps)")

    f_solution = open(log_root_dir + "solution1/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]) / 10)
    plt.plot(x, y, label = "CWND0")

    f_solution = open(log_root_dir + "solution2/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]) / 10)
    plt.plot(x, y, label = "CWND1")

    f_solution = open(log_root_dir + "solution3/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]) / 10)
    plt.plot(x, y, label = "CWND2")

    reno_data1 = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["send"]["total"], label = "tput0")
    reno_data2 = timeline(log_root_dir + "packet_log/", "192.168.1.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["send"]["total"], label = "tput1")
    reno_data3 = timeline(log_root_dir + "packet_log/", "192.168.2.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["send"]["total"], label = "tput2")

    f_router = open(log_root_dir + "router_log/router.log")
    x = []
    y = []
    for line in f_router.readlines():
        data = json.loads(line.replace("'", '"'))
        if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
            continue
        
        x.append(float(data["event_time"]))
        y.append(int(data["192.168.3.2"][1]) / 10)
    plt.plot(x, y, label = "router QUEUE")

    plt.legend()
    plt.savefig(log_root_dir + "timeline/RenoMulti.jpg")
    plt.close()