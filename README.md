benchmarking-cloud-storage-systems
==================================

benchcloud is a tool for benchmarking cloud storage systems.

Try it
------

    git clone git@github.com:zenja/benchmarking-cloud-storage-systems.git
    # pcapy is not listed in PyPI so far, install it from tarball instead:
    pip install "http://corelabs.coresecurity.com/index.php?module=Wiki&action=attachment&type=tool&page=Pcapy&file=pcapy-0.10.8.tar.gz"
    cd benchmarking-cloud-storage-systems
    pip install -r requirements.txt
    # You may want to sniff network traffic
    # by appending "-c benchcloud/example_benchmarking_conf/traffic_capture.conf"
    # to the end of the following commands:
    python -m benchcloud.benchcloud uploader -f benchcloud/example_benchmarking_conf/dropbox_random_upload_0.conf -a
    python -m benchcloud.benchcloud downloader -f benchcloud/example_benchmarking_conf/dropbox_download_0.conf
