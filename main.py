from example_test_utils import *

if __name__ == '__main__':

    print("single Reno stream test")
    print("--------------------------------------------------------------------------")
    single_reno_test("outputsinglereno/")
    print("--------------------------------------------------------------------------")

    print("single BBR stream test")
    print("--------------------------------------------------------------------------")
    single_bbr_test("outputsinglebbr/")
    print("--------------------------------------------------------------------------")

    print("multi Reno stream test")
    print("--------------------------------------------------------------------------")
    multi_reno_test("outputmultireno/")
    print("--------------------------------------------------------------------------")

    print("multi BBR stream test")
    print("--------------------------------------------------------------------------")
    multi_bbr_test("outputmultibbr/")
    print("--------------------------------------------------------------------------")

    print("DC top test")
    print("--------------------------------------------------------------------------")
    dc_top_test("outputDC/")
    print("--------------------------------------------------------------------------")

    # print("WAN top test")
    # print("--------------------------------------------------------------------------")
    # wan_top_test("outputWAN/")
    # print("--------------------------------------------------------------------------")

    # tar_interval_time = 0.05
    # tar_interval_count = 40

    # src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    # plt.title("Src Send")
    # plt.xlabel("Time(s)")
    # plt.ylabel("Rate(Mbps)")

    # for log in src_timeline_data["send"]:
    #     plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"][log], label = log)
    # plt.legend()
    # plt.savefig(log_root_dir + "timeline/SrcSend.jpg")
    # plt.close()

    # plt.title("Src Receive")
    # plt.xlabel("Time(s)")
    # plt.ylabel("Rate(Mbps)")

    # for log in src_timeline_data["receive"]:
    #     plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["receive"][log], label = log)
    # plt.legend()
    # plt.savefig(log_root_dir + "timeline/SrcReceive.jpg")
    # plt.close()

    # print("--------------------------------------------------------------------------")

    # tar_interval_time = 0.01
    # tar_interval_count = 2000

    # src_timeline_data = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)

    # plt.title("Reno Analyze")
    # plt.xlabel("Time(s)")
    # plt.ylabel("Rate(Mbps)")

    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["total"], label = "src total")
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], src_timeline_data["send"]["lost"], label = "src lost")

    # router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["total"], label = "router in")
    # router_in_data = timeline(log_root_dir + "packet_log/", "192.168.0.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_in_data["receive"]["lost"], label = "router drop")
    # router_out_data = timeline(log_root_dir + "packet_log/", "192.168.1.2", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], router_out_data["send"]["total"], label = "router out")

    # f_solution = open(log_root_dir + "solution/reno.log")
    # x = []
    # y = []
    # for line in f_solution.readlines():
    #     if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
    #         continue
    #     x.append(float(line.split(" ")[0]))
    #     y.append(float(line.split(" ")[1]) / 10)
    # plt.plot(x, y, label = "CWND")

    # f_router = open(log_root_dir + "router_log/router.log")
    # x = []
    # y = []
    # for line in f_router.readlines():
    #     data = json.loads(line.replace("'", '"'))
    #     if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
    #         continue
        
    #     x.append(float(data["event_time"]))
    #     y.append(int(data["192.168.1.2"][1]) / 10)
    # plt.plot(x, y, label = "router QUEUE")

    # plt.legend()
    # plt.savefig(log_root_dir + "timeline/RenoAnalyze.jpg")
    # plt.close()

    # tar_interval_time = 0.5
    # tar_interval_count = 160

    # plt.figure(figsize = (20,6))
    # plt.title("Multi Reno Analyze")
    # plt.xlabel("Time(s)")
    # plt.ylabel("Rate(Mbps)")

    # f_solution = open(log_root_dir + "solution1/reno.log")
    # x = []
    # y = []
    # for line in f_solution.readlines():
    #     if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
    #         continue
    #     x.append(float(line.split(" ")[0]))
    #     y.append(float(line.split(" ")[1]) / 10)
    # plt.plot(x, y, label = "CWND0")

    # f_solution = open(log_root_dir + "solution2/reno.log")
    # x = []
    # y = []
    # for line in f_solution.readlines():
    #     if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
    #         continue
    #     x.append(float(line.split(" ")[0]))
    #     y.append(float(line.split(" ")[1]) / 10)
    # plt.plot(x, y, label = "CWND1")

    # f_solution = open(log_root_dir + "solution3/reno.log")
    # x = []
    # y = []
    # for line in f_solution.readlines():
    #     if float(line.split(" ")[0]) >= tar_interval_count * tar_interval_time:
    #         continue
    #     x.append(float(line.split(" ")[0]))
    #     y.append(float(line.split(" ")[1]) / 10)
    # plt.plot(x, y, label = "CWND2")

    # reno_data1 = timeline(log_root_dir + "packet_log/", "192.168.0.1", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data1["send"]["total"], label = "tput0")
    # reno_data2 = timeline(log_root_dir + "packet_log/", "192.168.1.1", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data2["send"]["total"], label = "tput1")
    # reno_data3 = timeline(log_root_dir + "packet_log/", "192.168.2.1", tar_interval_time, tar_interval_count)
    # plt.plot([tar_interval_time * i for i in range(tar_interval_count)], reno_data3["send"]["total"], label = "tput2")

    # f_router = open(log_root_dir + "router_log/router.log")
    # x = []
    # y = []
    # for line in f_router.readlines():
    #     data = json.loads(line.replace("'", '"'))
    #     if float(data["event_time"]) >= tar_interval_count * tar_interval_time:
    #         continue
        
    #     x.append(float(data["event_time"]))
    #     y.append(int(data["192.168.3.2"][1]) / 10)
    # plt.plot(x, y, label = "router QUEUE")

    # plt.legend()
    # plt.savefig(log_root_dir + "timeline/RenoMulti.jpg")
    # plt.close()