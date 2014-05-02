from __future__ import print_function
import os
import sys
import time
import threading
from sys import stderr
from ConfigParser import SafeConfigParser

import pcapy


class Capturer(threading.Thread):
    def __init__(self, device, snaplen, promisc=False,
                 to_ms=0, filename="capture_data.pcap", cap_filter=None):
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
        #print("A new packet captured - timestamp: {}; capture length: {}; total length: {}".format(
        #    header.getts(), header.getcaplen(), header.getlen()))
        self.dumper.dump(header, data)


def from_conf(conf_filename):
    """Make a Capturer object from configuration file"""
    if os.path.exists(conf_filename):
        try:
            parser = SafeConfigParser()
            parser.read(conf_filename)
            device = parser.get('capture', 'device')
            snaplen = parser.getint('capture', 'snaplen')
            promisc = parser.getboolean('capture', 'promisc')
            to_ms = parser.getint('capture', 'to_ms')
            pcap_filename = parser.get('capture', 'filename')
            if parser.has_option('capture', 'filter'):
                cap_filter = parser.get('capture', 'filter')
            else:
                cap_filter = None
            capturer = Capturer(device=device, snaplen=snaplen, promisc=promisc,
                                to_ms=to_ms, cap_filter=cap_filter, filename=pcap_filename)
            return capturer
        except IOError:
            print("ERROR opening config file: {}".format(conf_filename))
            sys.exit(-1)
    else:
        print('The configure file does not exist: {}'.format(conf_filename))
        sys.exit(-1)

if __name__ == '__main__':
    # TODO: param to assign a conf file
    cap = Capturer('en0', snaplen=65535, to_ms=3000)
    cap.start()
    time.sleep(5)
    cap.stop_capture()
    cap.join()
