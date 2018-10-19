#!/usr/bin/python3
# -*- coding: iso-8859-15 -*-

import os
import datetime
import shutil

__author__ = "Markus M<E4>sker"
__email__ = "maesker@gmx.net"
__version__ = "1.0"
__status__ = "Development"


class Trace:

    def __init__(self, tracedir, flush=False, clear=False):
        self.tracedir = tracedir
        if clear and os.path.isdir(self.tracedir):
            shutil.rmtree(self.tracedir, True)  # ignore errors
        if not os.path.isdir(self.tracedir):
            os.makedirs(self.tracedir)
        self._write_cb = None
        self._flush_cb = None
        self.fp = None
        self._do_flush = flush
        self.open_tracefile()

        if self._do_flush:
            self.log = self.log_with_flush
        else:
            self.log = self.log_without_flush

    def get_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d-%H%M%S")

    def get_logtime(self):
        now = datetime.datetime.now()
        return "%s.%i" % (now.strftime("%Y%m%d-%H%M%S"), now.microsecond)

    def open_tracefile(self):
        logfile = os.path.join(self.tracedir, "%s.trace" % self.get_date())
        self.fp = open(logfile, 'w')
        self._write_cb = self.fp.write
        self._flush_cb = self.fp.flush

    def close_tracefile(self):
        assert self.fp is not None
        self.fp.flush()
        self.fp.close()

    def log_with_flush(self, cmd, msg):
        self._write_cb("%s: %8s: %s\n" % (self.get_logtime(), cmd, msg))
        self._flush_cb()

    def log_without_flush(self, cmd, msg):
        self._write_cb("%s: %8s: %s\n" % (self.get_logtime(), cmd, msg))
