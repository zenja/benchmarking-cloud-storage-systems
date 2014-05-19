import os
import argparse
from time import time, localtime, strftime

from benchcloud.drivers.dropbox_driver import DropboxDriver
from benchcloud.file_generators.random_file_generator import RandomFileGenerator


def log(msg):
    millis = int(round(time() * 1000))
    timestamp = "[{}] {} |".format(millis, strftime("%d %b %Y %H:%M:%S", localtime()))
    whole_message = "{} {}\n".format(timestamp, msg)
    print whole_message


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Upload a random-content file to dropbox')
    arg_parser.add_argument('-rf', action='store', dest='remote_filename', default='/target_file',
                            help='Local file', required=False)
    arg_parser.add_argument('-s', action='store', dest='file_size', help='File size', required=True)
    results = arg_parser.parse_args()
    remote_filename = results.remote_filename
    file_size = int(results.file_size)

    # generate file
    log('Start generating file...')
    file_generator = RandomFileGenerator(directory='./', delete=True)
    tmp_file = file_generator.make_file(size=file_size)
    log('File generated.')

    # rename file
    os.rename(tmp_file.name, 'target_file')

    # upload file
    dropbox = DropboxDriver()
    dropbox.connect()
    log('Starting uploading file to {}'.format(remote_filename))
    dropbox.upload(local_filename='./target_file', remote_filename=remote_filename)
    log('File uploading finished!')

    # close local file
    tmp_file.close()
