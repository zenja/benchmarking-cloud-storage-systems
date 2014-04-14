from __future__ import print_function
import time
import threading
from sys import stderr

import pcapy


class Capturer(threading.Thread):
    def __init__(self, device, snaplen, promisc=False,
                 to_ms=0, filename="capture_data", cap_filter=None):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.device = device
        self.snaplen = snaplen
        self.promisc = promisc
        self.to_ms = to_ms
        self.filename = filename
        self.cap_filter = cap_filter
        self.stop = False
        self.dumper = None

    def run(self):
        self.start_capture()

    def start_capture(self):
        self.stop = False
        pc = pcapy.open_live(self.device, self.snaplen, self.promisc, self.to_ms)
        if self.cap_filter is not None:
            pc.setfilter(self.cap_filter)
        self.dumper = pc.dump_open(self.filename)
        while not self.stop:
            try:
                header, data = pc.next()
                self._handle_packet(header, data)
            except pcapy.PcapError as e:
                print("[Warning] An error occurs when capturing a packet: {}".format(e.message),
                      file=stderr)
        print("Capture stopped.")

    def stop_capture(self):
        self.stop = True

    def _handle_packet(self, header, data):
        print("A new packet captured - timestamp: {}; capture length: {}; total length: {}".format(
            header.getts(), header.getcaplen(), header.getlen()))
        self.dumper.dump(header, data)

if __name__ == '__main__':
    cap = Capturer('en0', snaplen=65535, to_ms=3000)
    cap.start()
    time.sleep(5)
    cap.stop_capture()
    cap.join()
