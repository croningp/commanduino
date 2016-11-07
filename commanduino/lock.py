"""

.. module:: lock
   :platform: Unix
   :synopsis: Represents the specific threading functions to be carried out in this Library.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
import time
import threading


class Lock(object):
    """
    Represents the Threading locks to be used throughout this library.

    Args:
        timeout (int): Time to wait until timeout, default set to 1.

        sleep_time (float): Time to wait, default set to 0.001.

    """
    def __init__(self, timeout=1, sleep_time=0.001):
        self.lock = threading.Lock()
        self.timeout = timeout
        self.sleep_time = sleep_time

    def acquire(self):
        """
        Acquires a lock.
        """
        return self.lock.acquire()

    def release(self):
        """
        Releases a lock.
        """
        self.lock.release()

    def locked(self):
        """
        Checks if a thread is locked.

        Returns:
            self.lock.locked() (bool): Thread is locked/unlocked.
        """
        return self.lock.locked()

    def wait_until_released(self):
        """
        Waits until the thread lock is released.

        Returns:
            False (bool): Elapsed time > the timeout.

            True (bool): Elapsed time < timeout.

            elapsed (float): Time taken to complete.

        """
        elapsed = 0
        start_time = time.time()
        while self.locked():
            time.sleep(self.sleep_time)
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                return False, elapsed
        return True, elapsed

    def ensure_released(self):
        """
        Forces unlocking of a locked thread.
        """
        if self.locked():
            self.release()
