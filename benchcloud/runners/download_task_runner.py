import os
import sys
import importlib
import argparse
from time import time, localtime, strftime, sleep
from ConfigParser import SafeConfigParser

from prettytable import PrettyTable

import runner_util
from benchcloud.file_utils import file_util
from benchcloud.traffic import capturer


class DownloadTaskRunner(object):
    def __init__(self, conf_filename):
        self.load_conf(conf_filename)

        self.description = self.test_conf['description']
        self.sleep_enabled = self.parser.getboolean('test', 'sleep')
        if self.sleep_enabled:
            self.sleep_seconds = self.parser.getint('test', 'sleep_seconds')

        self.init_logging()
        self.operation_times = []
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
        self.test_conf = dict(self.parser.items('test'))
        self.driver_conf = dict(self.parser.items('driver'))

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
        for i, t in enumerate(self.operation_times):
            table_op_time.add_row(['#{}'.format(i), '{}ms'.format(t)])
        table_stat = PrettyTable(['Min', 'Max', 'Average'])
        table_stat.padding_width = 1
        t_min = min(self.operation_times)
        t_max = max(self.operation_times)
        t_avg = sum(self.operation_times) / len(self.operation_times)
        table_stat.add_row(['{}ms'.format(t) for t in (t_min, t_max, t_avg)])
        return '{}\n{}'.format(str(table_op_time), str(table_stat))

    def run(self):
        """Start running benchmark."""
        self.log("Start testing: {}".format(self.description))

        local_dir = self.test_conf['local_dir']
        remote_dir = self.test_conf['remote_dir']
        files_metadata = self.driver.list_files(remote_dir=remote_dir)
        num_normal_file = 0
        for i, file_md in enumerate(files_metadata):
            if file_md['is_dir']:
                continue

            remote_filename = file_md['path']
            local_filename = os.path.join(local_dir, file_util.path_leaf(remote_filename))
            self.log('')
            self.log(u"Start downloading file #{}: {}".format(num_normal_file, remote_filename))

            # download a file
            millis_start = int(round(time() * 1000))
            self.driver.download(remote_filename=file_md['path'], local_filename=local_filename)
            millis_end = int(round(time() * 1000))
            self.log("Operation finished. ({}ms)".format(millis_end-millis_start))
            self.operation_times.append(millis_end-millis_start)

            # Sleep
            if self.sleep_enabled:
                self.log("About to sleep for {} second(s)...".format(self.sleep_seconds))
                sleep(self.sleep_seconds)
                self.log("Sleep finished, now wake up.")

            # add num
            num_normal_file += 1
        self.log('')
        self.log('All {} operations finished! :)'.format(num_normal_file))

        # log statistics for operation time
        self.log_raw('\nStatistics of all operations:\n')
        statistics = self.make_statistics()
        self.log_raw(statistics)

        # print statistics
        print 'All operations finished!'
        print ''
        print statistics

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
