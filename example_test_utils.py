import os
import json
import matplotlib.pyplot as plt

from solution.sender.cc_solution.dctcp import DCTCP
from solution.sender.cc_solution.reno import Reno
from solution.sender.cc_solution.bbr import BBR
from solution.sender.block_scheduler_solution.fifo import FIFO
from solution.router.queue_scheduler_solution.sp import SP
from solution.router.queue_scheduler_solution.wrr import WRR
from solution.router.router_label_solution.ecn import ECN

from objects.simluator import Simluator

from config.constant import *

from utils import *
from log_utils import *

def single_abr_test(log_root_dir):

    net_trace1 = "dataset/link_trace/traceReno1.txt"
    net_trace2 = "dataset/link_trace/traceReno1.txt"
    net_trace3 = "dataset/link_trace/traceReno1.txt"
    net_trace4 = "dataset/link_trace/traceReno2.txt"

    abr_trace = "dataset/abr_trace/simple_test.txt"

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
        ],
        "abr": [
            ("192.168.0.1", "192.168.1.1", abr_trace)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    # tar_interval_time = 0.08
    # tar_interval_count = 500

    # src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    # fig = plt.figure(figsize = (12,6))
    # ax = fig.add_subplot(111)

    # lns1 = ax.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], "g", label = "Send Rate")

    # ax2 = ax.twinx()

    # f_solution = open(log_root_dir + "solution/reno.log")
    # x = []
    # y = []
    # for line in f_solution.readlines():
    #     if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
    #         continue
    #     x.append(float(line.split(" ")[0]))
    #     y.append(float(line.split(" ")[1]))
    # lns2 = ax2.plot(x, y, "r", label = "Reno CWND")

    # f_router = open(log_root_dir + "router_log/router1.log")
    # x = [tar_interval_time * i for i in range(tar_interval_count)]
    # y = [0 for i in range(tar_interval_count)]
    # cnt = [0 for i in range(tar_interval_count)]
    # for line in f_router.readlines():
    #     data = json.loads(line.replace("'", '"'))
    #     if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
    #         continue
        
    #     y[int(float(data["event_time"]) / tar_interval_time)] += int(data["192.168.1.2"][1])
    #     cnt[int(float(data["event_time"]) / tar_interval_time)] += 1
    # for i in range(tar_interval_count):
    #     y[i] /= cnt[i]
    # lns3 = ax2.plot(x, y, "b", label = "Router Queue")
    # lns = lns1+lns2+lns3
    # labs = [l.get_label() for l in lns]
    # ax.legend(lns, labs, loc=0, fontsize="x-large")

    # ax.set_xlabel("Time(s)", fontsize=15)
    # ax.set_ylabel("Rate(Mbps)", fontsize=15)
    # ax2.set_ylabel("CWND or Queue(pkts)", fontsize=15)
    # ax2.axes.set_ylim(0,45)

    # plt.savefig(log_root_dir + "timeline/RenoSingleTest.jpg")
    # plt.savefig(log_root_dir + "timeline/RenoSingleTest.pdf")
    # plt.close()  

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

    tar_interval_time = 0.08
    tar_interval_count = 500

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    fig = plt.figure(figsize = (12,6))
    ax = fig.add_subplot(111)

    lns1 = ax.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], "g", label = "Send Rate")

    ax2 = ax.twinx()

    f_solution = open(log_root_dir + "solution/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    lns2 = ax2.plot(x, y, "r", label = "Reno CWND")

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
    lns3 = ax2.plot(x, y, "b", label = "Router Queue")
    lns = lns1+lns2+lns3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0, fontsize="x-large")

    ax.set_xlabel("Time(s)", fontsize=15)
    ax.set_ylabel("Rate(Mbps)", fontsize=15)
    ax2.set_ylabel("CWND or Queue(pkts)", fontsize=15)
    ax2.axes.set_ylim(0,45)

    plt.savefig(log_root_dir + "timeline/RenoSingleTest.jpg")
    plt.savefig(log_root_dir + "timeline/RenoSingleTest.pdf")
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

    tar_interval_time = 0.1
    tar_interval_count = 400

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    fig = plt.figure(figsize = (12,6))
    ax = fig.add_subplot(111)

    lns1 = ax.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], "g", label = "Send Rate")

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
    lns3 = ax2.plot(x, y, "b", label = "Router Queue")
    lns = lns1+lns3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0, fontsize="x-large")

    ax.set_xlabel("Time(s)", fontsize=15)
    ax.set_ylabel("Rate(Mbps)", fontsize=15)
    ax2.set_ylabel("Queue(pkts)", fontsize=15)

    plt.savefig(log_root_dir + "timeline/BBRSingleTest.jpg")
    plt.savefig(log_root_dir + "timeline/BBRSingleTest.pdf")
    plt.close()

def multi_reno_test2(log_root_dir):

    net_trace = "dataset/link_trace/trace1.txt"
    send_trace = "dataset/link_trace/sender.txt"

    block_trace1 = "dataset/block_trace/queuetest1.txt"
    block_trace2 = "dataset/block_trace/queuetest2.txt"
    block_trace3 = "dataset/block_trace/queuetest3.txt"

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
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2", "192.168.2.2", "192.168.3.2"], [50, 50, 50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2", "192.168.2.0/24" : "192.168.2.2", "192.168.3.0/24" : "192.168.3.2"}, WRR(), 2.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", send_trace),
            ("192.168.1.1", "192.168.1.2", send_trace),
            ("192.168.2.1", "192.168.2.2", send_trace),
            ("192.168.3.1", "192.168.3.2", net_trace),
            ("192.168.0.2", "192.168.0.1", net_trace),
            ("192.168.1.2", "192.168.1.1", net_trace),
            ("192.168.2.2", "192.168.2.1", net_trace),
            ("192.168.3.2", "192.168.3.1", net_trace)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.3.1", block_trace1),
            ("192.168.1.1", "192.168.3.1", block_trace2),
            ("192.168.2.1", "192.168.3.1", block_trace3)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    tar_interval_time = 0.1
    tar_interval_count = 400

    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("CWND(pkts)", fontsize=15)

    f_solution = open(log_root_dir + "solution1/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    plt.plot(x, y, label = "CWND0")

    f_solution = open(log_root_dir + "solution2/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    plt.plot(x, y, label = "CWND1")

    f_solution = open(log_root_dir + "solution3/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    plt.plot(x, y, label = "CWND2")

    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/WeightedCWNDTest.jpg")
    plt.savefig(log_root_dir + "timeline/WeightedCWNDTest.pdf")
    plt.close()

    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("Rate(Mbps)", fontsize=15)

    reno_data1 = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["send"]["total"], label = "TPUT0")
    reno_data2 = timeline(log_root_dir + "packet_log/", "192.168.1.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["send"]["total"], label = "TPUT1")
    reno_data3 = timeline(log_root_dir + "packet_log/", "192.168.2.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["send"]["total"], label = "TPUT2")

    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/WeightedTPUTTest.jpg")
    plt.savefig(log_root_dir + "timeline/WeightedTPUTTest.pdf")
    plt.close()

def multi_reno_test(log_root_dir):

    net_trace = "dataset/link_trace/tracemultireno.txt"

    block_trace1 = "dataset/block_trace/FULLReno1.txt"
    block_trace2 = "dataset/block_trace/FULLReno2.txt"
    block_trace3 = "dataset/block_trace/FULLReno3.txt"

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
            ("192.168.0.1", "192.168.3.1", block_trace1),
            ("192.168.1.1", "192.168.3.1", block_trace2),
            ("192.168.2.1", "192.168.3.1", block_trace3)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    tar_interval_time = 0.5
    tar_interval_count = 600

    plt.figure(figsize = (15,6))
    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("CWND(pkts)", fontsize=15)

    f_solution = open(log_root_dir + "solution1/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    plt.plot(x, y, label = "CWND0")

    f_solution = open(log_root_dir + "solution2/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    plt.plot(x, y, label = "CWND1")

    f_solution = open(log_root_dir + "solution3/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    plt.plot(x, y, label = "CWND2")

    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/RenoMultiCWNDTest.jpg")
    plt.savefig(log_root_dir + "timeline/RenoMultiCWNDTest.pdf")
    plt.close()

    plt.figure(figsize = (15,6))
    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("Rate(Mbps)", fontsize=15)

    reno_data1 = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["send"]["total"], label = "TPUT0")
    reno_data2 = timeline(log_root_dir + "packet_log/", "192.168.1.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["send"]["total"], label = "TPUT1")
    reno_data3 = timeline(log_root_dir + "packet_log/", "192.168.2.1", tar_interval_time, tar_interval_count)
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["send"]["total"], label = "TPUT2")

    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/RenoMultiTPUTTest.jpg")
    plt.savefig(log_root_dir + "timeline/RenoMultiTPUTTest.pdf")
    plt.close()

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

    block_trace0 = "dataset/block_trace/FULLWAN1.txt"
    block_trace1 = "dataset/block_trace/FULLWAN2.txt"
    block_trace2 = "dataset/block_trace/FULLWAN3.txt"

    if os.path.exists(log_root_dir):
        del_all(log_root_dir)
    os.makedirs(log_root_dir)
    os.makedirs(log_root_dir + "solution1/")
    os.makedirs(log_root_dir + "solution2/")
    os.makedirs(log_root_dir + "solution3/")
    os.makedirs(log_root_dir + "timeline/")

    config_dict = {
        "nodes": [
            (objectType.SENDER, "SRC1 & DST2", "192.168.0.1", FIFO(), Reno()), 
            (objectType.SENDER, "SRC2 & DST3", "192.168.1.1", FIFO(), Reno()), 
            (objectType.SENDER, "SRC3 & DST1", "192.168.2.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "10.0.1.1", "10.0.2.1"], [50, 50], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "10.0.2.1", "192.168.2.0/24" : "10.0.1.1"}, SP(), 32.0),
            (objectType.ROUTER, "router2", ["192.168.1.2", "10.0.2.2", "10.0.3.1"], [50, 50], {"192.168.1.0/24" : "192.168.1.2", "192.168.0.0/24" : "10.0.2.2", "192.168.2.0/24" : "10.0.3.1"}, SP(), 32.0),
            (objectType.ROUTER, "router3", ["192.168.2.2", "10.0.3.2", "10.0.1.2"], [50, 50], {"192.168.2.0/24" : "192.168.2.2", "192.168.0.0/24" : "10.0.1.2", "192.168.1.0/24" : "10.0.3.2"}, SP(), 32.0)
        ],
        "edges": [
            ("192.168.0.1", "192.168.0.2", net_trace),
            ("192.168.0.2", "192.168.0.1", net_trace),
            ("192.168.1.1", "192.168.1.2", net_trace),
            ("192.168.1.2", "192.168.1.1", net_trace),
            ("192.168.2.2", "192.168.2.1", net_trace),
            ("192.168.2.1", "192.168.2.2", net_trace),
            ("10.0.1.1", "10.0.1.2", net_trace),
            ("10.0.1.2", "10.0.1.1", net_trace),
            ("10.0.2.1", "10.0.2.2", net_trace),
            ("10.0.2.2", "10.0.2.1", net_trace),
            ("10.0.3.1", "10.0.3.2", net_trace),
            ("10.0.3.2", "10.0.3.1", net_trace)
        ],
        "blocks": [
            ("192.168.0.1", "192.168.2.1", block_trace0),
            ("192.168.1.1", "192.168.0.1", block_trace1),
            ("192.168.2.1", "192.168.1.1", block_trace2)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()

    tar_interval_time = 0.1
    tar_interval_count = 400

    reno_data1 = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)
    reno_data2 = timeline(log_root_dir + "packet_log/", "192.168.1.1", tar_interval_time, tar_interval_count)
    reno_data3 = timeline(log_root_dir + "packet_log/", "192.168.2.1", tar_interval_time, tar_interval_count)
    
    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("Rate(Mbps)", fontsize=15)

    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["send"]["total"], label = "SEND0")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["send"]["total"], label = "SEND1")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["send"]["total"], label = "SEND2")
    
    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/WANSENDTest.jpg")
    plt.savefig(log_root_dir + "timeline/WANSENDTest.pdf")
    plt.close()

    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("Rate(Mbps)", fontsize=15)

    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["receive"]["total"], label = "RECV0")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["receive"]["total"], label = "RECV1")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["receive"]["total"], label = "RECV2")

    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/WANRECVTest.jpg")
    plt.savefig(log_root_dir + "timeline/WANRECVTest.pdf")
    plt.close()


def dc_top_test(log_root_dir):

    net_trace = "dataset/link_trace/trace1.txt"

    block_trace0 = "dataset/block_trace/FULLDC1.txt"
    block_trace1 = "dataset/block_trace/FULLDC2.txt"

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
            (objectType.ROUTER, "switch1", ["10.0.0.2", "10.0.1.2", "10.0.2.2"], [50, 50], {"10.0.0.0/24" : "10.0.0.2", "10.0.1.0/24" : "10.0.1.2", "10.0.2.0/24" : "10.0.2.2", "10.1.0.0/16" : "10.0.2.2"}, SP(), 32.0),
            (objectType.ROUTER, "switch2", ["10.1.0.2", "10.1.1.2", "10.1.2.2"], [50, 50], {"10.1.0.0/24" : "10.1.0.2", "10.1.1.0/24" : "10.1.1.2", "10.1.2.0/24" : "10.1.2.2", "10.0.0.0/16" : "10.1.2.2"}, SP(), 32.0),
            (objectType.ROUTER, "router1", ["10.1.2.1", "10.0.2.1"], [50, 50], {"10.0.0.0/16" : "10.0.2.1", "10.1.0.0/16" : "10.1.2.1"}, SP(), 32.0)
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
            ("10.1.1.1", "10.0.1.1", block_trace1)
        ]
    }

    testsimluator = Simluator(config_dict, log_root_dir)
    testsimluator.run()


    tar_interval_time = 0.1
    tar_interval_count = 400

    reno_data1 = timeline(log_root_dir + "packet_log/", "10.0.0.1", tar_interval_time, tar_interval_count)
    reno_data2 = timeline(log_root_dir + "packet_log/", "10.1.0.1", tar_interval_time, tar_interval_count)
    reno_data3 = timeline(log_root_dir + "packet_log/", "10.1.1.1", tar_interval_time, tar_interval_count)
    reno_data4 = timeline(log_root_dir + "packet_log/", "10.0.1.1", tar_interval_time, tar_interval_count)

    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("Rate(Mbps)", fontsize=15)

    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["send"]["total"], label = "SEND1")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["send"]["total"], label = "SEND2")
    
    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/DCSENDTest.jpg")
    plt.savefig(log_root_dir + "timeline/DCSENDTest.pdf")
    plt.close()

    plt.xlabel("Time(s)", fontsize=15)
    plt.ylabel("Rate(Mbps)", fontsize=15)

    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["receive"]["total"], label = "RECV1")
    plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data4["receive"]["total"], label = "RECV2")

    plt.legend(fontsize="x-large", loc = 9)
    plt.savefig(log_root_dir + "timeline/DCRECVTest.jpg")
    plt.savefig(log_root_dir + "timeline/DCRECVTest.pdf")
    plt.close()

def dctcp_test(log_root_dir):

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
            (objectType.SENDER, "SRC1", "192.168.0.1", FIFO(), DCTCP(log_root_dir + "solution/")), 
            (objectType.SENDER, "DST1", "192.168.1.1", FIFO(), Reno()), 
            (objectType.ROUTER, "router1", ["192.168.0.2", "192.168.1.2"], [25, 25], {"192.168.0.0/24" : "192.168.0.2", "192.168.1.0/24" : "192.168.1.2"}, SP(), 2.0, ECN())
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

    tar_interval_time = 0.08
    tar_interval_count = 500

    src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    fig = plt.figure(figsize = (12,6))
    ax = fig.add_subplot(111)

    lns1 = ax.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], "g", label = "Send Rate")

    ax2 = ax.twinx()

    f_solution = open(log_root_dir + "solution/reno.log")
    x = []
    y = []
    for line in f_solution.readlines():
        if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
            continue
        x.append(float(line.split(" ")[0]))
        y.append(float(line.split(" ")[1]))
    lns2 = ax2.plot(x, y, "r", label = "Reno CWND")

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
    lns3 = ax2.plot(x, y, "b", label = "Router Queue")
    lns = lns1+lns2+lns3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0, fontsize="x-large")

    ax.set_xlabel("Time(s)", fontsize=15)
    ax.set_ylabel("Rate(Mbps)", fontsize=15)
    ax2.set_ylabel("CWND or Queue(pkts)", fontsize=15)
    ax2.axes.set_ylim(0,45)

    plt.savefig(log_root_dir + "timeline/DCTCPSingleTest.jpg")
    plt.savefig(log_root_dir + "timeline/DCTCPSingleTest.pdf")
    plt.close()