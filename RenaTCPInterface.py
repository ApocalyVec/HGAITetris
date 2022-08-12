import zmq


rena_server_add_dsp_worker_request = 1
rena_server_update_worker_request = 2
rena_server_remove_worker_request = 3
rena_server_exit_request = 4

class RenaTCPObject:
    def __init__(self, data, processor_dict=None, exit_process=False):
        self.data = data
        self.processor_dict = processor_dict
        self.exit_process = exit_process


class RenaTCPRequestObject:
    def __init__(self, request_type):
        self.request_type = request_type


class RenaTCPAddDSPWorkerRequestObject(RenaTCPRequestObject):
    def __init__(self, stream_name, port_id, identity, processor_dict):
        super().__init__(request_type=rena_server_add_dsp_worker_request)
        self.stream_name = stream_name
        self.port_id = port_id
        self.identity = identity
        self.processor_dict = processor_dict


class RenaTCPUpdateDSPWorkerRequestObject(RenaTCPRequestObject):
    def __init__(self, stream_name, group_format, processor_dict):
        super().__init__(request_type=rena_server_update_worker_request)
        self.stream_name = stream_name
        self.group_format = group_format
        self.processor_dict = processor_dict


class RenaTCPRemoveWorkerRequestObject(RenaTCPRequestObject):
    def __init__(self, stream_name, group_format, processor_dict):
        super().__init__(request_type=rena_server_remove_worker_request)
        self.stream_name = stream_name
        self.group_format = group_format
        self.processor_dict = processor_dict

class RenaTCPExitServerRequestObject(RenaTCPRequestObject):
    def __init__(self):
        super().__init__(request_type=rena_server_exit_request)

class RenaTCPInterface:

    def __init__(self, stream_name, port_id, identity, pattern='request-reply', add_poller=False):
        self.bind_header = "tcp://*:%s"
        self.connect_header = 'tcp://localhost:'

        self.stream_name = stream_name
        self.port_id = port_id
        self.identity = identity

        self.pattern = pattern
        if pattern == 'request-reply' and identity == 'server': socket_type = zmq.REP
        elif pattern == 'request-reply' and identity == 'client': socket_type = zmq.REQ
        elif pattern == 'pipeline' and identity == 'client': socket_type = zmq.PULL
        elif pattern == 'pipeline' and identity == 'server': socket_type = zmq.PUSH
        elif pattern == 'router-dealer' and identity == 'client': socket_type = zmq.DEALER
        elif pattern == 'router-dealer' and identity == 'server': socket_type = zmq.ROUTER
        else: raise AttributeError('Unsupported interface pattern: {0} or identity {1}'.format(pattern, identity))

        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        if identity == 'server': self.bind_socket()
        elif identity == 'client': self.connect_socket()
        else: raise AttributeError('Unsupported interface identity: {0}'.format(identity))

        # create poller object, so we can poll msg with a timeout
        if add_poller:
            self.poller = zmq.Poller()
            self.poller.register(self.socket, zmq.POLLIN)
        else:
            self.poller = None

    def bind_socket(self):
        binder = self.bind_header % self.port_id
        self.socket.bind(binder)

    def connect_socket(self):
        connection = self.connect_header + str(self.port_id)
        self.socket.connect(connection)

        # return pickle.loads(p)

    def process_data(self):
        pass

    def send_string(self, data: str, *args, **kwargs):
        self.socket.send(data.encode('utf-8'), *args, **kwargs)

    def recv_string(self, *args, **kwargs):
        return self.socket.recv(*args, **kwargs).decode('utf-8')

    def __del__(self):
        self.socket.close()
        self.context.term()

def recv_string_router(socket_interface, is_block):
    if is_block:
        routing_id, message = socket_interface.socket.recv_multipart(flags=0)
        return message.decode('utf-8'), routing_id
    else:
        try:
            routing_id, message = socket_interface.socket.recv_multipart(
                flags=zmq.NOBLOCK)
            return message.decode('utf-8'), routing_id
        except zmq.error.Again:
            return None  # no message has arrived at the socket yet