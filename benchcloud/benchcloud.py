import sys

from runners import upload_task_runner


def handle_uploader(extra_args):
    upload_task_runner.main(prog='uploader', args=extra_args)


def handle_help():
    print 'Help: to be built...'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python benchcloud.py COMMAND [extra args]'
        sys.exit(-1)
    command = sys.argv[1]
    if command == 'uploader':
        handle_uploader(sys.argv[2:])
    elif command == 'help':
        handle_help()
    else:
        print 'Command not supported: {}'.format(command)
        sys.exit(-1)
