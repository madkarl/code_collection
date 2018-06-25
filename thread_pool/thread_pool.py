#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time
from enum import Enum


class ThreadStatus(Enum):
    waiting = 0
    working = 1

class ThreadPool(object):

    def __init__(self, thread_count = None, work_app = None):
        def processor_count():
            return 1
        self._thread_count = thread_count if isinstance(thread_count, int) else (processor_count() * 2 + 2)
        if not work_app:
            raise Exception("param error.")
        self._work_app = work_app
        self._stop_single = False
        self._thread_list = []
        self._result_list = []
        for x in range(thread_count):
            thread_obj = threading.Thread(target=self._main, args=(len(self._thread_list), ))
            thread_obj.start()
            self._thread_list.append(thread_obj)

    def _main(self, index):
        thread_index = index
        print("waiting thread at @", thread_index)

    def query_free_thread(self):
        return False

    def wait_finish(self):
        while 1:
            time.sleep(1)
        self._stop_single = True

if __name__ == '__main__':
    def demo_app():
        print('hello')
    tp = ThreadPool(2, demo_app)
    tp.wait_finish()
    print("finish")