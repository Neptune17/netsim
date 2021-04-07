from solution.sender.cc import CongestionControl

class Reno(CongestionControl):

    def ack_event(self):
        return 
    
    def drop_event(self):
        return 
    
    def send_event(self, sender):
        
        result = {
            "USE_CWND" : False,
            "PADDING_RATE" : 12.0
        }

        sender.cc_solution_cache = result

        return 