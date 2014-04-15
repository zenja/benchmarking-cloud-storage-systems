from benchcloud.drivers.dropbox_driver import DropboxDriver
from benchcloud.operators.uploader import Uploader
from benchcloud.file_generators.random_file_generator import RandomFileGenerator


if __name__ == '__main__':
    driver = DropboxDriver()
    driver.connect()
    uploader = Uploader(server_driver=driver)
    generator = RandomFileGenerator(prefix='benchmarking-', suffix='', delete=True)
    for n in range(10):
        file_obj = generator.make_file(size=102400)
        uploader.upload(local_filename=file_obj.name, remote_dir="/benchmark-test")
        file_obj.close()
