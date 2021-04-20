from solution.sender.cc import CongestionControl

class Reno(CongestionControl):

    def __init__(self, log_path = None):
        super(Reno, self).__init__()
        self.ssthresh = float("inf")
        self.curr_state = "slow_start"
        self.states = ["slow_start", "congestion_avoidance", "fast_recovery"]
        self.ack_nums = 0

        self.cur_time = -1
        self.last_cwnd = 0
        self.instant_drop_nums = 0
        self.USE_CWND = True
        self.cwnd = 1

        self.last_decision_time = 0.0

        self.log_path = log_path

    def ack_event(self, event_time):
        
        self.cur_time = event_time
        self.last_cwnd = self.cwnd

        self.ack_nums += 1
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
            "USE_CWND" : True,
            "CWND" : self.cwnd
        }

        sender.cc_solution_cache = result

        return 