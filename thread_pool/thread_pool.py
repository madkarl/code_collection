#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time
import copy
import inspect
import ctypes
from queue import Queue

class ThreadPool(object):

    def __init__(self, thread_count = None):
        def processor_count():
            return 1
        self._thread_count = thread_count if isinstance(thread_count, int) else (processor_count() * 2 + 2)
        self._thread_stop = False
        self._thread_list = []
        for x in range(thread_count):
            thread_obj = threading.Thread(target=self._main, args=(len(self._thread_list), ))
            thread_obj.start()
            self._thread_list.append(thread_obj)
        self._task_list = Queue()
        self._task_count = 0
        self._result_lock = threading.Lock()
        self._result_list = []

    def _main(self, index):
        thread_index = index
        # print("waiting work at #%d" % thread_index)
        while not self._thread_stop:
            time.sleep(1)
            task = self._get_task()
            if task:
                app = task[0]
                args = task[1]
                kw = task[2]
                # print("thread", thread_index, " get new task", app, args, kw)
                ret = app(*args, **kw)
                self._add_result((ret, thread_index, app, args, kw))

    def _get_task(self):
        data = None
        if not self._task_list.empty():
            data = self._task_list.get(timeout=0)
        return data

    def add_task(self, app, *args, **kw):
        self._task_list.put((app, args, kw))
        self._task_count += 1

    def get_task_count(self):
        return self._task_list.qsize()

    def _add_result(self, result):
        if self._result_lock.acquire():
            self._result_list.append(result)
            self._result_lock.release()

    def get_result(self):
        if self._result_lock.acquire():
            ret = copy.deepcopy(self._result_list)
            self._result_lock.release()
            return ret
        return []

    def get_result_count(self):
        ret = 0
        if self._result_lock.acquire():
            ret = len(self._result_list)
            self._result_lock.release()
        return ret

    def stop_thread(self, thread):
        def _async_raise(tid, exctype):
            tid = ctypes.c_long(tid)
            if not inspect.isclass(exctype):
                exctype = type(exctype)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
            if res == 0:
                raise ValueError("invalid thread id")
            elif res != 1:
                # """if it returns a number greater than one, you're in trouble,
                # and you should call it again with exc=NULL to revert the effect"""
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        self._async_raise(thread.ident, SystemExit)

    def wait_finish(self):
        while self.get_task_count() > 0 or \
            self._task_count != self.get_result_count():
            time.sleep(0.5)

        self._thread_stop = True
        for x in self._thread_list:
            if x.isAlive():
                x.join()


if __name__ == '__main__':
    def demo_app(a, b, *, kk=3):
        ret = a + b + kk
        for x in range(5):
            print('demo app ret:', ret)
            time.sleep(1)
        return (ret, "it's ok = %d" % ret)

    tp = ThreadPool(2)
    tp.add_task(demo_app, 1, 2, kk=3)
    tp.add_task(demo_app, 2, 3, kk=4)
    tp.add_task(demo_app, 3, 4, kk=5)
    tp.wait_finish()
    print("finish")