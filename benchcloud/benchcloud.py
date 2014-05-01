import sys

from runners import upload_task_runner
from runners import download_task_runner


def handle_uploader(extra_args):
    upload_task_runner.main(prog='uploader', args=extra_args)


def handle_downloader(extra_args):
    download_task_runner.main(prog='downloader', args=extra_args)


def handle_help(extra_args):
    print 'Help: to be built...'


command_map = {
    'uploader': handle_uploader,
    'downloader': handle_downloader,
    'help': handle_help
}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python benchcloud.py COMMAND [extra args]'
        sys.exit(-1)
    command = sys.argv[1]
    if command in command_map:
        command_map[command](sys.argv[2:])
    else:
        print 'Command not supported: {}'.format(command)
        sys.exit(-1)

