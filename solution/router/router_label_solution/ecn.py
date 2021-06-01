from solution.router.router_label import RouterLabel

class ECN(RouterLabel):

    def router_out_label(self, router, port_id):
        
        if len(router.queues[port_id][1]) > router.queue_size[port_id][1] * 0.8:
            router.label_solution_cache = True
            return
        router.label_solution_cache = False
        return 