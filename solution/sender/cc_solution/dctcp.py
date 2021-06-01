from solution.sender.cc import CongestionControl

class DCTCP(CongestionControl):

    def __init__(self, log_path = None):
        super(DCTCP, self).__init__()
        self.ssthresh = float("inf")
        self.curr_state = "slow_start"
        self.states = ["slow_start", "congestion_avoidance", "fast_recovery"]
        self.ack_nums = 0

        self.cur_time = -1
        self.last_cwnd = 0
        self.instant_drop_nums = 0
        self.USE_CWND = True
        self.cwnd = 1

        self.log_path = log_path

        self.dctcp_alpha = 0
        self.F_total = 0
        self.F_ecn = 0

    def update_alpha(self, new_alpha):
        self.dctcp_alpha = self.dctcp_alpha * 0.9 + new_alpha * 0.1

    def update_F(self, ecn):
        if ecn:
            self.F_ecn += 1
        self.F_total += 1
        if self.F_total > self.cwnd:
            self.update_alpha(self.F_ecn / self.F_total)
            self.F_total = 0
            self.F_ecn = 0

    def ack_event(self, event_time, data):
        
        ecn = data["ECN"]

        self.update_F(ecn)

        self.cur_time = event_time
        self.last_cwnd = self.cwnd

        self.ack_nums += 1
        if ecn:
            delta = self.cwnd - int(self.cwnd * (1 - self.dctcp_alpha / 2))
            self.ack_nums -= delta
            if self.ack_nums < 0:
                self.ack_nums = 0
            self.cwnd = int(self.cwnd * (1 - self.dctcp_alpha / 2))

        if self.curr_state == self.states[0]:
            if self.ack_nums == self.cwnd:
                self.cwnd *= 2
                self.ack_nums = 0
            if self.cwnd >= self.ssthresh:
                self.curr_state = self.states[1]

        elif self.curr_state == self.states[1]:
            if self.ack_nums == self.cwnd:
                self.cwnd += 1
                self.ack_nums = 0

        if self.log_path != None:
            f = open(self.log_path + "reno.log", "a+")
            print(event_time, self.cwnd, file = f)
            f.close()

        return 
    
    def drop_event(self, event_time):
        
        if self.cur_time < event_time:
            self.last_cwnd = 0
            self.instant_drop_nums = 0

        if self.instant_drop_nums > 0:
            return
        self.instant_drop_nums += 1
        self.curr_state = self.states[2]
        self.ack_nums = 0
        if self.last_cwnd > 0 and self.last_cwnd != self.cwnd:
            self.cwnd = self.last_cwnd
            self.last_cwnd = 0

        if self.curr_state == self.states[2]:
            self.ssthresh = max(self.cwnd // 2, 1)
            self.cwnd = self.ssthresh
            self.curr_state = self.states[1]

        self.cur_time = event_time

        if self.log_path != None:
            f = open(self.log_path + "reno.log", "a+")
            print(event_time, self.cwnd, file = f)
            f.close()

        return 
    
    def send_event(self, sender):
        
        result = {
            "CWND" : self.cwnd
        }

        sender.cc_solution_cache = result

        return 