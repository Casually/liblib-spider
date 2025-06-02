from threading import Lock

class AtomicCounter:
    def __init__(self, initial=0):
        self.value = initial
        self.lock = Lock()

    def add(self, amount):
        with self.lock:
            self.value += amount
            return self.value
