import os
import importlib
import json
import sys
import argparse
from time import time, localtime, strftime, sleep
from ConfigParser import SafeConfigParser

from prettytable import PrettyTable


class Runner(object):
    def __init__(self, conf_filename):
        self.load_conf(conf_filename)

        self.description = self.test_conf['description']
        self.times = self.parser.getint('test', 'times')
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
        self.test_conf = dict(self.parser.items('test'))
        self.driver_conf = dict(self.parser.items('driver'))
        self.operator_conf = dict(self.parser.items('operator'))
        self.file_generator_conf = dict(self.parser.items('file_generator'))
        self.file_generator_conf['size'] = int(self.file_generator_conf['size'])
        self.file_generator_conf['delete'] = self.parser.get('file_generator', 'delete')

    def init_logging(self):
        self.logging_enabled = self.parser.getboolean('logging', 'enabled')
        if self.logging_enabled:
            log_filename = self.parser.get('logging', 'log_file')
            self.logfile_obj = open(log_filename, mode='w', buffering=0)

    def load_testers(self):
        # driver
        driver_module_name, driver_class_name = Runner.parse_class(self.driver_conf['class'])
        driver_module = importlib.import_module(driver_module_name)
        driver_class = getattr(driver_module, driver_class_name)
        self.driver = driver_class()
        self.driver.connect()

        # operator
        operator_module_name, operator_class_name = Runner.parse_class(self.operator_conf['class'])
        operator_module = importlib.import_module(operator_module_name)
        operator_class = getattr(operator_module, operator_class_name)
        self.operator = operator_class(server_driver=self.driver)

        # file generator
        generator_module_name, generator_class_name = Runner.parse_class(self.file_generator_conf['class'])
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
        file_size = int(self.file_generator_conf['size'])
        operation_method = getattr(self.operator, self.operator_conf['operation_method'])
        for n in range(self.times):
            self.log('')
            self.log("Start operation #{}".format(n))

            # Generate file
            self.log('Generating file...')
            millis_start = int(round(time() * 1000))
            file_obj = self.file_generator.make_file(size=file_size)
            millis_end = int(round(time() * 1000))
            self.log("File generated: {} ({}ms)".format(file_obj.name, millis_end-millis_start))

            # Execute operation
            operation_method_params = self.get_operation_method_params(file_obj)
            self.log('About to execute operation...')
            millis_start = int(round(time() * 1000))
            operation_method(**operation_method_params)
            millis_end = int(round(time() * 1000))
            self.log("Operation finished. ({}ms)".format(millis_end-millis_start))
            self.operation_times.append(millis_end-millis_start)

            # Close file object
            file_obj.close()
            self.log("File object closed: {}".format(file_obj.name))

            # Sleep
            if self.sleep_enabled:
                self.log("About to sleep for {} second(s)...".format(self.sleep_seconds))
                sleep(self.sleep_seconds)
                self.log("Sleep finished, now wake up.")
        self.log('')
        self.log('All {} operations finished! :)'.format(self.times))

        # log statistics for operation time
        self.log_raw('\nStatistics of all operations:\n')
        statistics = self.make_statistics()
        self.log_raw(statistics)

        # print statistics
        print 'All operations finished!'
        print ''
        print statistics

    def get_operation_method_params(self, file_obj):
        result = json.loads(self.operator_conf['operation_method_params'])
        for k, v in result.iteritems():
            if "<generated_file.name>".lower() == v.lower():
                result[k] = file_obj.name
        return result

    @staticmethod
    def parse_class(path):
        parts = path.split('.')
        module_name = '.'.join(parts[:-1])
        class_name = parts[-1]
        return module_name, class_name

    def auth_driver(self):
        """Acquire authentication info needed to use driver"""
        self.driver.acquire_access_token()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Execute benchmarking predefined in a configuration file.')
    arg_parser.add_argument('-f', action='store', dest='conf_filename', help='Configuration file', required=True)
    arg_parser.add_argument('-a', action='store_true', default=False, dest='auth', help='Make authentication')
    results = arg_parser.parse_args()
    conf_filename = results.conf_filename
    runner = Runner(conf_filename)
    if results.auth:
        runner.auth_driver()
    runner.run()
