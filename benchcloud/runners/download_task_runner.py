import os
import sys
import importlib
import argparse
import Queue
from threading import Thread
from time import time, localtime, strftime, sleep
from ConfigParser import SafeConfigParser

from prettytable import PrettyTable

import runner_util
from benchcloud.file_utils import file_util
from benchcloud.traffic import capturer


class DownloadTaskRunner(object):
    def __init__(self, conf_filename):
        self.load_conf(conf_filename)

        # init task queue, log queue, operation_times map
        # element in task queue: (seq, remote_filename, local_filename)
        self.task_queue = Queue.Queue()
        self.log_queue = Queue.Queue()
        # {operation sequence -> operation time in milliseconds, ...}
        self.operation_times = {}

        self.init_logging()
        self.load_testers()

    def load_conf(self, filename):
        """Load configuration file."""
        if os.path.exists(filename):
            try:
                self.parser = SafeConfigParser()
                self.parser.read(filename)
            except IOError:
                print "ERROR opening config file: {}".format(filename)
                sys.exit(1)
        else:
            print 'The configure file does not exist: {}'.format(filename)

        # driver conf
        self.driver_conf = dict(self.parser.items('driver'))

        # basic test conf
        self.test_conf = dict(self.parser.items('test'))
        self.description = self.test_conf['description']
        self.sleep_enabled = self.parser.getboolean('test', 'sleep')
        if self.sleep_enabled:
            self.sleep_seconds = self.parser.getint('test', 'sleep_seconds')

        # concurrent conf
        if self.parser.has_section('concurrent') and self.parser.has_option('concurrent', 'threads'):
            self.task_thread_num = max(1, self.parser.getint('concurrent', 'threads'))
        else:
            self.task_thread_num = 1

    def init_logging(self):
        self.logging_enabled = self.parser.getboolean('logging', 'enabled')
        if self.logging_enabled:
            log_filename = self.parser.get('logging', 'log_file')
            self.logfile_obj = open(log_filename, mode='w', buffering=0)

    def load_testers(self):
        # driver
        driver_module_name, driver_class_name = runner_util.parse_class(self.driver_conf['class'])
        driver_module = importlib.import_module(driver_module_name)
        driver_class = getattr(driver_module, driver_class_name)
        self.driver = driver_class()
        self.driver.connect()

    def log(self, message):
        millis = int(round(time() * 1000))
        timestamp = "[{}] {} |".format(millis, strftime("%d %b %Y %H:%M:%S", localtime()))
        whole_message = u"{} {}\n".format(timestamp, message)
        self.log_raw(whole_message)

    def log_raw(self, raw_message):
        self.logfile_obj.write(raw_message.encode('utf8'))

    def make_statistics(self):
        """Make statistics for operation time

        Return:
            A pretty message showing the statistics
        """
        table_op_time = PrettyTable(['Operation', 'Time'])
        table_op_time.padding_width = 1
        for i, t in self.operation_times.iteritems():
            table_op_time.add_row(['#{}'.format(i), '{}ms'.format(t)])
        table_stat = PrettyTable(['Min', 'Max', 'Average'])
        table_stat.padding_width = 1
        t_min = min(self.operation_times.itervalues())
        t_max = max(self.operation_times.itervalues())
        t_avg = sum(self.operation_times.itervalues()) / len(self.operation_times)
        table_stat.add_row(['{}ms'.format(t) for t in (t_min, t_max, t_avg)])
        return '{}\n{}'.format(str(table_op_time), str(table_stat))

    def download_worker(self):
        """A thread worker for downloading files one by one from task queue.

        Should be a daemon thread.
        """
        while True:
            # get task
            operation_seq, remote_filename, local_filename = self.task_queue.get()
            self.log_queue.put(u'Start downloading file #{}: {}'.format(operation_seq, remote_filename))

            # download the file
            millis_start = int(round(time() * 1000))
            self.driver.download(remote_filename=remote_filename, local_filename=local_filename)
            millis_end = int(round(time() * 1000))
            self.log_queue.put("Operation #{} finished. ({}ms)".format(operation_seq, millis_end-millis_start))
            self.operation_times[operation_seq] = millis_end-millis_start

            # notify that the task is handled
            self.task_queue.task_done()

            # Sleep
            if self.sleep_enabled:
                self.log_queue.put("Operation #{}: About to sleep for {} second(s)...".format(
                    operation_seq, self.sleep_seconds))
                sleep(self.sleep_seconds)
                self.log_queue.put("Operation #{}: Sleep finished, now wake up.".format(operation_seq))

    def log_worker(self):
        """A thread worker for reading logging msg from msg queue and writing to log file.

        Note that the log thread should be a daemon thread.
        """
        while True:
            log_msg = self.log_queue.get()
            self.log(log_msg)

    def run(self):
        # start log thread
        log_thread = Thread(target=self.log_worker)
        log_thread.setDaemon(True)
        log_thread.start()

        self.log("Start testing: {}".format(self.description))

        # bookkeeping start time for all operations
        millis_start = int(round(time() * 1000))

        # sending all tasks into task queue
        # a task is just a number indication its operation sequence
        local_dir = self.test_conf['local_dir']
        remote_dir = self.test_conf['remote_dir']
        files_metadata = self.driver.list_files(remote_dir=remote_dir)
        num_regular_file = 0
        for i, file_md in enumerate(files_metadata):
            if file_md['is_dir']:
                continue
            remote_filename = file_md['path']
            local_filename = os.path.join(local_dir, file_util.path_leaf(remote_filename))
            self.task_queue.put((num_regular_file, remote_filename, local_filename))
            num_regular_file += 1
        num_operation = num_regular_file - 1

        print "Number of operation: {}".format(num_operation)

        # starting task worker threads
        for i in range(self.task_thread_num):
            t = Thread(target=self.download_worker)
            t.setDaemon(True)
            t.start()

        print "invoking task_queue.join()..."

        # wait for all tasks to be handled
        self.task_queue.join()

        # get total amount of time spent for all operations
        millis_end = int(round(time() * 1000))
        millis_total = millis_end - millis_start

        print "task_queue.join() returned"

        # all operations should have finished now,
        # do not need to put to log queue first
        self.log('\nAll {} operations finished! :)'.format(num_operation))

        # log statistics for operation time
        self.log_raw('\nStatistics of all operations:\n')
        statistics = self.make_statistics()
        self.log_raw(statistics)
        self.log('Time spent for all operations: {}ms'.format(millis_total))

        # print statistics
        print 'All operations finished!'
        print ''
        print statistics
        print '\n'

    def auth_driver(self):
        """Acquire authentication info needed to use driver"""
        self.driver.acquire_access_token()

def main(prog=None, args=None):
    arg_parser = argparse.ArgumentParser(
        prog=prog,
        description='Downloader: Execute benchmarking predefined in a configuration file.')
    arg_parser.add_argument('-f', action='store', dest='conf_filename', help='Configuration file', required=True)
    arg_parser.add_argument('-a', action='store_true', default=False, dest='auth', help='Make authentication')
    arg_parser.add_argument('-c', action='store', dest='capturer_conf_filename', default='', help='Capturer configuration file')
    results = arg_parser.parse_args(args=args)
    conf_filename = results.conf_filename
    runner = DownloadTaskRunner(conf_filename)
    if results.auth:
        runner.auth_driver()
    if results.capturer_conf_filename:
        the_capturer = capturer.from_conf(results.capturer_conf_filename)
        the_capturer.start()
    runner.run()


if __name__ == '__main__':
    main(sys.argv[1:])
