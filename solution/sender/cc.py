class CongestionControl:

    def ack_event(self, event_time):
        return 
    
    def drop_event(self, event_time):
        return 
    
    def send_event(self, sender):
        
        result = {
            "USE_CWND" : False,
            "PADDING_RATE" : 12.0
        }

        sender.cc_solution_cache = result

        return 