import queue
from enum import Enum
from collections import defaultdict, deque

from .bank import Bank

class BankRequestStage(Enum):
    # incoming = 1 # Maybe use this to signal earlier?
    start = 2
    finish_success = 3
    finish_fail = 4
    term = 255

class BankRequest:
    def __init__(self, holder, type, data, stage):
        self.holder = holder
        self.type = type
        self.data = data
        self.stage = stage

    def __eq__(self, b):
        if not isinstance(b, BankRequest): return False
        return (self.holder, self.type, self.data, self.stage) == (b.holder, b.type, b.data, b.stage)

    def __str__(self):
        return 'BankRequest(%s, %s, %s, %s)'%(self.holder, self.type, self.data, self.stage)

    @classmethod
    def term_request(cls):
        return cls(None, None, None, stage=BankRequestStage.term)

class BankHandler:
    def __init__(self):
        self.requests = queue.Queue()
        self.impl = Bank()
        self.account_locks = defaultdict(deque)

    def request(self, request):
        self.requests.put(request)

    def handle(self, request):
        name = request.data[0]
        lock_deque = self.account_locks[name]
        if request.stage == BankRequestStage.start:
            if not lock_deque or lock_deque[0].holder == request.holder:
                if not lock_deque:
                    lock_deque.append(request)
                result = getattr(self.impl, request.type)(*request.data)
                request.holder.result_queue.put(result, block=False)
                return True
        elif request.stage == BankRequestStage.finish_fail or request.stage == BankRequestStage.finish_success:
            if lock_deque and lock_deque[0].holder == request.holder:
                lock_deque.popleft()
                self.impl.finalize(name, request.stage == BankRequestStage.finish_success)
                return True
            else:
                raise Exception('Finish request that is not locked')
        lock_deque.append(request)
        return False

    def termination_hook(self):
        def terminate():
            self.requests.put(BankRequest.term_request())
        return terminate

    def serve_forever(self):
        serving = True
        while True:
            try:
                request = self.requests.get(block=serving)
            except queue.Empty as e:
                break
            if request.stage == BankRequestStage.term:
                serving = False
                continue
            if not self.handle(request):
                self.requests.put(request, block=False)
