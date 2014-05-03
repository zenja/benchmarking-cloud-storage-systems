import os
import sys
import importlib
import json
import argparse
import Queue
from threading import Thread
from time import time, localtime, strftime, sleep
from ConfigParser import SafeConfigParser

from prettytable import PrettyTable

import runner_util
from benchcloud.traffic import capturer


class UploadTaskRunner(object):
    def __init__(self, conf_filename):
        self.load_conf(conf_filename)

        # init task queue, log queue, operation_times map
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

        # operation conf
        self.operator_conf = dict(self.parser.items('operator'))

        # file generator conf
        self.file_generator_conf = dict(self.parser.items('file_generator'))
        self.file_generator_conf['size'] = int(self.file_generator_conf['size'])
        self.file_generator_conf['delete'] = self.parser.get('file_generator', 'delete')

        # basic test conf
        self.test_conf = dict(self.parser.items('test'))
        self.description = self.test_conf['description']
        self.times = self.parser.getint('test', 'times')
        self.sleep_enabled = self.parser.getboolean('test', 'sleep')
        if self.sleep_enabled:
            self.sleep_seconds = self.parser.getint('test', 'sleep_seconds')

        # concurrent conf
        if self.parser.has_section('concurrent') and self.parser.has_option('concurrent', 'threads'):
            self.task_thread_num = max(1, min(self.times, self.parser.getint('concurrent', 'threads')))
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

        # operator
        operator_module_name, operator_class_name = runner_util.parse_class(self.operator_conf['class'])
        operator_module = importlib.import_module(operator_module_name)
        operator_class = getattr(operator_module, operator_class_name)
        self.operator = operator_class(server_driver=self.driver)

        # file generator
        generator_module_name, generator_class_name = runner_util.parse_class(self.file_generator_conf['class'])
        generator_module = importlib.import_module(generator_module_name)
        generator_class = getattr(generator_module, generator_class_name)
        self.file_generator = generator_class(**self.file_generator_conf)

    def log(self, message):
        millis = int(round(time() * 1000))
        timestamp = "[{}] {} |".format(millis, strftime("%d %b %Y %H:%M:%S", localtime()))
        whole_message = "{} {}\n".format(timestamp, message)
        self.log_raw(whole_message)

    def log_raw(self, raw_message):
        self.logfile_obj.write(raw_message)

    def make_statistics(self):
        """Make statistics for operation time

        Return:
            A pretty message showing the statistics
        """
        result = ''
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

    def upload_worker(self):
        """A thread worker for uploading files one by one from task queue.

        Should be a daemon thread.
        """
        file_size = int(self.file_generator_conf['size'])
        operation_method = getattr(self.operator, self.operator_conf['operation_method'])
        while True:
            operation_seq = self.task_queue.get()

            self.log_queue.put('\nStart operation #{}'.format(operation_seq))

            # Generate file
            self.log_queue.put('Operation #{}: Generating file...'.format(operation_seq))
            millis_start = int(round(time() * 1000))
            file_obj = self.file_generator.make_file(size=file_size)
            millis_end = int(round(time() * 1000))
            self.log_queue.put("Operation #{}: File generated: {} ({}ms)".format(
                operation_seq, file_obj.name, millis_end-millis_start))

            # Execute operation
            operation_method_params = self.get_operation_method_params(file_obj)
            self.log_queue.put('Operation #{}: About to execute operation...'.format(operation_seq))
            millis_start = int(round(time() * 1000))
            operation_method(**operation_method_params)
            millis_end = int(round(time() * 1000))
            self.log_queue.put("Operation #{} finished. ({}ms)".format(operation_seq, millis_end-millis_start))
            self.operation_times[operation_seq] = millis_end-millis_start

            # Close file object
            file_obj.close()
            self.log("Operation #{}: File object closed: {}".format(operation_seq, file_obj.name))

            # notify the queue that we have finished this task
            self.task_queue.task_done()

            # Sleep
            if self.sleep_enabled:
                self.log("Operation #{}: About to sleep for {} second(s)...".format(
                    operation_seq, self.sleep_seconds))
                sleep(self.sleep_seconds)
                self.log("Operation #{}: Sleep finished, now wake up.".format(operation_seq))

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

        self.log_queue.put("Start testing: {}".format(self.description))

        # sending all tasks into task queue
        # a task is just a number indication its operation sequence
        for seq in range(self.times):
            self.task_queue.put(seq)

        # bookkeeping start time for all operations
        millis_start = int(round(time() * 1000))

        # starting task worker threads
        for i in range(self.task_thread_num):
            t = Thread(target=self.upload_worker)
            t.setDaemon(True)
            t.start()

        # wait for all tasks to be handled
        self.task_queue.join()

        # get total amount of time spent for all operations
        millis_end = int(round(time() * 1000))
        millis_total = millis_end - millis_start

        # all operations should have finished now
        # do no need to put to log queue first
        self.log('\nAll {} operations finished! :)'.format(self.times))

        # log statistics for operation time
        self.log_raw('\nStatistics of all operations:\n')
        statistics = self.make_statistics()
        self.log_raw(statistics)
        self.log_raw('\n')
        self.log('Time spent for all operations: {}ms'.format(millis_total))

        # print statistics
        print 'All operations finished!'
        print ''
        print statistics
        print '\n'
        print 'Time spent for all operations: {}ms'.format(millis_total)

    def get_operation_method_params(self, file_obj):
        result = json.loads(self.operator_conf['operation_method_params'])
        for k, v in result.iteritems():
            if "<generated_file.name>".lower() == v.lower():
                result[k] = file_obj.name
        return result

    def auth_driver(self):
        """Acquire authentication info needed to use driver"""
        self.driver.acquire_access_token()


def main(prog=None, args=None):
    arg_parser = argparse.ArgumentParser(
        prog=prog,
        description='Uploader: Execute benchmarking predefined in a configuration file.')
    arg_parser.add_argument('-f', action='store', dest='conf_filename', help='Configuration file', required=True)
    arg_parser.add_argument('-a', action='store_true', default=False, dest='auth', help='Make authentication')
    arg_parser.add_argument('-c', action='store', dest='capturer_conf_filename', default='', help='Capturer configuration file')
    results = arg_parser.parse_args(args=args)
    conf_filename = results.conf_filename
    runner = UploadTaskRunner(conf_filename)
    if results.auth:
        runner.auth_driver()
    if results.capturer_conf_filename:
        the_capturer = capturer.from_conf(results.capturer_conf_filename)
        the_capturer.start()
    runner.run()


if __name__ == '__main__':
    main(sys.argv[1:])
