import time
import threading


class Lock(object):

    def __init__(self, timeout=1, sleep_time=0.001):
        self.lock = threading.Lock()
        self.timeout = timeout
        self.sleep_time = sleep_time

    def acquire(self):
        return self.lock.acquire()

    def release(self):
        self.lock.release()

    def locked(self):
        return self.lock.locked()

    def wait_until_released(self):
        elapsed = 0
        start_time = time.time()
        while self.locked():
            time.sleep(self.sleep_time)
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                return False, elapsed
        return True, elapsed

    def ensure_released(self):
        if self.locked():
            self.release()
