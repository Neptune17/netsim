import json

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
            if log["Src_IP"] != tar_ip and log["Dest_IP"] != tar_ip:
                continue
            if log["Src_IP"] == tar_ip:
                ret["send"]["total"] += 1
                if log["Dropped"]:
                    ret["send"]["lost"] += 1
                if log["Retrans"]:
                    ret["send"]["retrans"] += 1
                if log["Ack"]:
                    ret["send"]["ack"] += 1
                if not log["Retrans"] and not log["Ack"]:
                    ret["send"]["norm"] += 1
            if log["Dest_IP"] == tar_ip:
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