# -*- coding: utf-8 -*-

import threading

class Thread(threading.Thread):
    def __init__(self, target, *args):
        self.target = target
        self.args = args
        threading.Thread.__init__(self)


    def run(self):
        self.target(*self.args)
