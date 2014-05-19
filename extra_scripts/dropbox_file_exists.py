import os
import argparse
from time import time, localtime, strftime, sleep

from benchcloud.drivers.dropbox_driver import DropboxDriver


def log(msg):
    millis = int(round(time() * 1000))
    timestamp = "[{}] {} |".format(millis, strftime("%d %b %Y %H:%M:%S", localtime()))
    whole_message = "{} {}".format(timestamp, msg)
    print whole_message


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Test if a file exists in Dropbox')
    arg_parser.add_argument('-rf', action='store', dest='remote_filename', default='/target_file',
                            help='Local file', required=False)
    results = arg_parser.parse_args()
    remote_filename = results.remote_filename
    local_filename = './downloaded_target_file'

    # delete old target file
    if os.path.isfile(local_filename):
        os.remove(local_filename)

    # Test if file exists
    dropbox = DropboxDriver()
    dropbox.connect()
    while True:
        log('Start to download file')
        dropbox.download(remote_filename=remote_filename, local_filename=local_filename)
        log('Operation finished!')
        if os.path.isfile(local_filename):
            break
        sleep(0.5)
    log('File downloaded successfully!')
