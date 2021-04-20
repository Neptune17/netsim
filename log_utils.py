import json
import math

def parse_packet_logs(tar_path, index):
    compose_data = []
    try:
        file_name = tar_path + "packet-" + str(index) + ".log"
        with open(file_name, 'r') as f:
            for line in f.readlines():
                compose_data.append(json.loads(line.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null").replace(" inf", " \"inf\"")))
    except FileNotFoundError:
        print("Log index out of range")
    except json.decoder.JSONDecodeError as e:
        print(str(e))
        print(line.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null").replace(" inf", " \"inf\""))
    finally:
        return compose_data

def packet_statistics(tar_path, tar_ip):
    
    ret = {}
    ret["Tar_IP"] = tar_ip
    ret["send"] = {}
    ret["receive"] = {}
    ret["send"]["total"] = 0
    ret["send"]["lost"] = 0
    ret["send"]["retrans"] = 0
    ret["send"]["ack"] = 0
    ret["send"]["norm"] = 0
    ret["receive"]["total"] = 0
    ret["receive"]["lost"] = 0
    ret["receive"]["retrans"] = 0
    ret["receive"]["ack"] = 0
    ret["receive"]["norm"] = 0

    index = 1
    while(True):
        
        log_data = parse_packet_logs(tar_path, index)
        index += 1

        if len(log_data) == 0:
            break

        for log in log_data:
            for extralog in log["extra"]["LOG_info"]:
                if extralog[2] == tar_ip:
                    if extralog[3] == "out":
                        ret["send"]["total"] += 1
                        if log["Dropped"]:
                            ret["send"]["lost"] += 1
                        if log["Retrans"]:
                            ret["send"]["retrans"] += 1
                        if log["Ack"]:
                            ret["send"]["ack"] += 1
                        if not log["Retrans"] and not log["Ack"]:
                            ret["send"]["norm"] += 1
                    if extralog[3] == "in":
                        ret["receive"]["total"] += 1
                        if log["Dropped"]:
                            ret["receive"]["lost"] += 1
                        if log["Retrans"]:
                            ret["receive"]["retrans"] += 1
                        if log["Ack"]:
                            ret["receive"]["ack"] += 1
                        if not log["Retrans"] and not log["Ack"]:
                            ret["receive"]["norm"] += 1
        
    return ret

def timeline(tar_path, tar_ip, interval_time, interval_count):
    ret = {}
    ret["Tar_IP"] = tar_ip
    ret["Interval_time"] = interval_time
    ret["Interval_count"] = interval_count
    ret["send"] = {}
    ret["receive"] = {}
    ret["send"]["total"] = [0.0 for _ in range(interval_count)]
    ret["send"]["lost"] = [0.0 for _ in range(interval_count)]
    ret["send"]["retrans"] = [0.0 for _ in range(interval_count)]
    ret["send"]["ack"] = [0.0 for _ in range(interval_count)]
    ret["send"]["norm"] = [0.0 for _ in range(interval_count)]
    ret["receive"]["total"] = [0.0 for _ in range(interval_count)]
    ret["receive"]["lost"] = [0.0 for _ in range(interval_count)]
    ret["receive"]["retrans"] = [0.0 for _ in range(interval_count)]
    ret["receive"]["ack"] = [0.0 for _ in range(interval_count)]
    ret["receive"]["norm"] = [0.0 for _ in range(interval_count)]

    index = 1
    while(True):
        
        log_data = parse_packet_logs(tar_path, index)
        index += 1

        if len(log_data) == 0:
            break

        for log in log_data:
            for extralog in log["extra"]["LOG_info"]:
                if extralog[2] == tar_ip:
                    timeline_index = math.floor(extralog[0] / interval_time)
                    if timeline_index >= interval_count:
                        continue
                    if timeline_index < 0:
                        print("Timeline Error", timeline_index)
                    if extralog[3] == "out":
                        ret["send"]["total"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if log["Dropped"]:
                            ret["send"]["lost"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if log["Retrans"]:
                            ret["send"]["retrans"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if log["Ack"]:
                            ret["send"]["ack"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if not log["Retrans"] and not log["Ack"]:
                            ret["send"]["norm"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                    if extralog[3] == "in":
                        ret["receive"]["total"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if log["Dropped"]:
                            ret["receive"]["lost"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if log["Retrans"]:
                            ret["receive"]["retrans"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if log["Ack"]:
                            ret["receive"]["ack"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time
                        if not log["Retrans"] and not log["Ack"]:
                            ret["receive"]["norm"][timeline_index] += log["Size"] * 8 / 10**6 / interval_time

    return ret