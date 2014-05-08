benchmarking-cloud-storage-systems
==================================

benchcloud is a tool for benchmarking cloud storage systems.

Install
------

Mac OS X

    git clone git@github.com:zenja/benchmarking-cloud-storage-systems.git
    # pcapy is not listed in PyPI so far, install it from tarball instead:
    pip install "http://corelabs.coresecurity.com/index.php?module=Wiki&action=attachment&type=tool&page=Pcapy&file=pcapy-0.10.8.tar.gz"
    cd benchmarking-cloud-storage-systems
    pip install -r requirements.txt

Ubuntu

    git clone git@github.com:zenja/benchmarking-cloud-storage-systems.git
    sudo apt-get install python-dev python-pcapy
    cd benchmarking-cloud-storage-systems
    pip install -r requirements.txt

Start Benchmarking
------------------

    # 1. You may want to sniff network traffic
    # by appending "-c benchcloud/example_benchmarking_conf/traffic_capture.conf"
    # to the following commands.
    # 2. The ``-a'' option will ask you to authorize benchcloud to access your data in the cloud,
    # which is needed for the first time you use benchcloud to access data in a cloud service.
    # 3. Check the conf file before benchmarking to make sure the remote directory/file exists.

    # Sample benchmark for uploading files
    python -m benchcloud.benchcloud uploader -f benchcloud/example_benchmarking_conf/dropbox_random_upload_0.conf -a

    # Sample benchmark for downloading files
    python -m benchcloud.benchcloud downloader -f benchcloud/example_benchmarking_conf/dropbox_download_0.conf
