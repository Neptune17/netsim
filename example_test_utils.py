import os
import json
import matplotlib.pyplot as plt

from solution.sender.cc_solution.reno import Reno
from solution.sender.cc_solution.bbr import BBR
from solution.sender.block_scheduler_solution.fifo import FIFO
from solution.router.queue_scheduler_solution.sp import SP

from objects.simluator import Simluator

from config.constant import *

from utils import *
from log_utils import *

def single_reno_test(log_root_dir):

    net_trace1 = "dataset/link_trace/traceReno1.txt"
    net_trace2 = "dataset/link_trace/traceReno1.txt"
    net_trace3 = "dataset/link_trace/traceReno1.txt"
    net_trace4 = "dataset/link_trace/traceReno2.txt"

    block_trace1 = "dataset/block_trace/FULL0.txt"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1", "192.168.0.1", FIFO(), Reno(log_root_dir + "solution/")), 
            (objectType.SENDER, "DST1", "192.168.1.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2"], [25, 25], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2"}, SP(), 2.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", net_trace1),
            ("192.168.1.1", "192.168.1.2", net_trace2),
            ("192.168.0.2", "192.168.0.1", net_trace3),
            ("192.168.1.2", "192.168.1.1", net_trace4)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.1.1", block_trace1)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    print(json.dumps(packet_statistics(log_root_dir + "packet_log/", "192.168.0.1"), indent=4))
    print(json.dumps(packet_statistics(log_root_dir + "packet_log/", "192.168.1.1"), indent=4))

    tar_interval_time = 0.08
    tar_interval_count = 500

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    fig = plt.figure(figsize = (12,6))
    ax = fig.add_subplot(111)

    # plt.title("Reno Single Stream")
    # plt.xlabel("Time(s)")
    # plt.ylabel("Rate(Mbps)")

    lns1 = ax.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], "g", label = "Send Rate")
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["lost"], label = "src lost")

    # router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["total"], label = "router in")
    # router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["lost"], label = "router drop")
    # router_out_data = timeline(log_root_dir + "packet_log/", "192.168.1.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_out_data["send"]["total"], label = "router out")

    ax2 = ax.twinx()

    f_solution = open(log_root_dir + "solution/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    lns2 = ax2.plot(x, y, label = "Reno CWND")

    f_router = open(log_root_dir + "router_log/router1.log")
    x = [tar_interval_time * i for i in range(tar_interval_count)]
    y = [0 for i in range(tar_interval_count)]
    cnt = [0 for i in range(tar_interval_count)]
    for line in f_router.readlines():
        data = json.loads(line.replace("'", '"'))
        if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
            continue
        
        y[int(float(data["event_time"]) / tar_interval_time)] += int(data["192.168.1.2"][1])
        cnt[int(float(data["event_time"]) / tar_interval_time)] += 1
    for i in range(tar_interval_count):
        y[i] /= cnt[i]
    lns3 = ax2.plot(x, y, "y", label = "Router Queue")
    lns = lns1+lns2+lns3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0, fontsize="x-large")

    ax.set_xlabel("Time(s)", fontsize=15)
    ax.set_ylabel("Rate(Mbps)", fontsize=15)
    ax2.set_ylabel("CWND or Queue(pkts)", fontsize=15)

    plt.savefig(log_root_dir + "timeline/RenoSingle.jpg")
    plt.savefig(log_root_dir + "timeline/RenoSingle.pdf")
    plt.close()

def single_bbr_test(log_root_dir):
    
    net_trace1 = "dataset/link_trace/traceBBR1.txt"
    net_trace2 = "dataset/link_trace/traceBBR1.txt"
    net_trace3 = "dataset/link_trace/traceBBR1.txt"
    net_trace4 = "dataset/link_trace/traceBBR2.txt"

    block_trace1 = "dataset/block_trace/FULL0.txt"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1", "192.168.0.1", FIFO(), BBR(log_root_dir + "solution/")), 
            (objectType.SENDER, "DST1", "192.168.1.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2"], [25, 25], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2"}, SP(), 2.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", net_trace1),
            ("192.168.1.1", "192.168.1.2", net_trace2),
            ("192.168.0.2", "192.168.0.1", net_trace3),
            ("192.168.1.2", "192.168.1.1", net_trace4)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.1.1", block_trace1)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    print(json.dumps(packet_statistics(log_root_dir + "packet_log/", "192.168.0.1"), indent=4))
    print(json.dumps(packet_statistics(log_root_dir + "packet_log/", "192.168.1.1"), indent=4))

    tar_interval_time = 0.08
    tar_interval_count = 500

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    fig = plt.figure(figsize = (12,6))
    ax = fig.add_subplot(111)

    # plt.title("Reno Single Stream")
    # plt.xlabel("Time(s)")
    # plt.ylabel("Rate(Mbps)")

    lns1 = ax.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], "g", label = "Send Rate")
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["lost"], label = "src lost")

    # router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["total"], label = "router in")
    # router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["lost"], label = "router drop")
    # router_out_data = timeline(log_root_dir + "packet_log/", "192.168.1.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_out_data["send"]["total"], label = "router out")

    ax2 = ax.twinx()

    f_router = open(log_root_dir + "router_log/router1.log")
    x = [tar_interval_time * i for i in range(tar_interval_count)]
    y = [0 for i in range(tar_interval_count)]
    cnt = [0 for i in range(tar_interval_count)]
    for line in f_router.readlines():
        data = json.loads(line.replace("'", '"'))
        if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
            continue
        
        y[int(float(data["event_time"]) / tar_interval_time)] += int(data["192.168.1.2"][1])
        cnt[int(float(data["event_time"]) / tar_interval_time)] += 1
    for i in range(tar_interval_count):
        y[i] /= cnt[i]
    lns3 = ax2.plot(x, y, "y", label = "Router Queue")
    lns = lns1+lns3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0, fontsize="x-large")

    ax.set_xlabel("Time(s)", fontsize=15)
    ax.set_ylabel("Rate(Mbps)", fontsize=15)
    ax2.set_ylabel("Queue(pkts)", fontsize=15)

    plt.savefig(log_root_dir + "timeline/BBRSingle.jpg")
    plt.savefig(log_root_dir + "timeline/BBRSingle.pdf")
    plt.close()

def multi_reno_test(log_root_dir):

    net_trace = "dataset/link_trace/trace1.txt"

    block_trace0 = "dataset/block_trace/FULL0.txt"
    block_trace5 = "dataset/block_trace/FULL1.txt"
    block_trace10 = "dataset/block_trace/FULL2.txt"

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
            (objectType.SENDER, "DST1", "192.168.3.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2", "192.168.2.2", "192.168.3.2"], [50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2", "192.168.2.0/24" : "192.168.2.2", "192.168.3.0/24" : "192.168.3.2"}, SP(), 2.0)
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

def multi_bbr_test(log_root_dir):

    net_trace = "dataset/link_trace/trace1.txt"

    block_trace0 = "dataset/block_trace/FULL0.txt"
    block_trace5 = "dataset/block_trace/FULL1.txt"
    block_trace10 = "dataset/block_trace/FULL2.txt"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution1/")
    os.makedirs(log_root_dir + "solution2/")
    os.makedirs(log_root_dir + "solution3/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1", "192.168.0.1", FIFO(), BBR(log_root_dir + "solution1/")), 
            (objectType.SENDER, "SRC2", "192.168.1.1", FIFO(), BBR(log_root_dir + "solution2/")), 
            (objectType.SENDER, "SRC3", "192.168.2.1", FIFO(), BBR(log_root_dir + "solution3/")), 
            (objectType.SENDER, "DST1", "192.168.3.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2", "192.168.2.2", "192.168.3.2"], [50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2", "192.168.2.0/24" : "192.168.2.2", "192.168.3.0/24" : "192.168.3.2"}, SP(), 2.0)
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

def wan_top_test(log_root_dir):

    net_trace = "dataset/link_trace/trace1.txt"

    block_trace0 = "dataset/block_trace/FULL0.txt"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution1/")
    os.makedirs(log_root_dir + "solution2/")
    os.makedirs(log_root_dir + "solution3/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1", "192.168.0.1", FIFO(), BBR(log_root_dir + "solution1/")), 
            (objectType.SENDER, "SRC2", "192.168.1.1", FIFO(), BBR(log_root_dir + "solution2/")), 
            (objectType.SENDER, "SRC3", "192.168.2.1", FIFO(), BBR(log_root_dir + "solution3/")), 
            (objectType.SENDER, "DST1", "192.168.3.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2", "192.168.2.2", "192.168.3.2"], [50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2", "192.168.2.0/24" : "192.168.2.2", "192.168.3.0/24" : "192.168.3.2"}, SP(), 2.0)
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
            ("192.168.1.1", "192.168.3.1", block_trace0),
            ("192.168.2.1", "192.168.3.1", block_trace0)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

def dc_top_test(log_root_dir):

    net_trace = "dataset/link_trace/trace1.txt"

    block_trace0 = "dataset/block_trace/FULL0.txt"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution1/")
    os.makedirs(log_root_dir + "solution2/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1", "10.0.0.1", FIFO(), Reno(log_root_dir + "solution1/")), 
            (objectType.SENDER, "SRC2", "10.1.1.1", FIFO(), Reno(log_root_dir + "solution2/")), 
            (objectType.SENDER, "DST1", "10.1.0.1", FIFO(), Reno()), 
            (objectType.SENDER, "DST2", "10.0.1.1", FIFO(), Reno()), 
            (objectType.ROUTER, "switch1", ["10.0.0.2", "10.0.1.2", "10.0.2.2"], [50, 50], {"10.0.0.0/24" : "10.0.0.2", "10.0.1.0/24" : "10.0.1.2", "10.0.2.0/24" : "10.0.2.2", "10.1.0.0/16" : "10.0.2.2"}, SP(), 2.0),
            (objectType.ROUTER, "switch2", ["10.1.0.2", "10.1.1.2", "10.1.2.2"], [50, 50], {"10.1.0.0/24" : "10.1.0.2", "10.1.1.0/24" : "10.1.1.2", "10.1.2.0/24" : "10.1.2.2", "10.0.0.0/16" : "10.1.2.2"}, SP(), 2.0),
            (objectType.ROUTER, "router1", ["10.1.2.1", "10.0.2.1"], [50, 50], {"10.0.0.0/16" : "10.0.2.1", "10.1.0.0/16" : "10.1.2.1"}, SP(), 2.0)
        ],
        "edges": [
            ("10.0.0.1", "10.0.0.2", net_trace),
            ("10.0.0.2", "10.0.0.1", net_trace),
            ("10.0.1.1", "10.0.1.2", net_trace),
            ("10.0.1.2", "10.0.1.1", net_trace),
            ("10.0.2.2", "10.0.2.1", net_trace),
            ("10.0.2.1", "10.0.2.2", net_trace),
            ("10.1.0.1", "10.1.0.2", net_trace),
            ("10.1.0.2", "10.1.0.1", net_trace),
            ("10.1.1.1", "10.1.1.2", net_trace),
            ("10.1.1.2", "10.1.1.1", net_trace),
            ("10.1.2.2", "10.1.2.1", net_trace),
            ("10.1.2.1", "10.1.2.2", net_trace)
        ],
        "blocks": [
            ("10.0.0.1", "10.1.0.1", block_trace0),
            ("10.1.1.1", "10.0.1.1", block_trace0)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()