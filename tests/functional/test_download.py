from drivers.dropbox_driver import DropboxDriver
from operators.downloader import Downloader
from file_generators.random_file_generator import RandomFileGenerator

if __name__ == '__main__':
    dbox = DropboxDriver()
    dbox.connect(include_guest=False)
    downloader = Downloader(server_driver=dbox)
    downloader.download(local_dir='./', remote_filename='/tmp/oven.xml')
    downloader.download(local_filename='./oven-copy.xml', remote_filename='/tmp/oven.xml')
