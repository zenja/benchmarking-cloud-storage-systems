from benchcloud.drivers.dropbox_driver import DropboxDriver
from benchcloud.operators.uploader import Uploader
from benchcloud.file_generators.random_file_generator import RandomFileGenerator

if __name__ == '__main__':
    dbox = DropboxDriver()
    dbox.connect(include_guest=False)
    uploader = Uploader(server_driver=dbox)
    generator = RandomFileGenerator(directory='./', prefix='benchmarking-')
    file_obj = generator.make_file(size=10240, delete=True)
    uploader.upload(local_filename=file_obj.name)
    file_obj.close()
    uploader.upload_dir('./', '/benchmark-test')
