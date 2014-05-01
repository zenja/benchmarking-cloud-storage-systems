benchmarking-cloud-storage-systems
==================================

benchcloud is a tool for benchmarking cloud storage systems.

Try it
------

    git clone git@github.com:zenja/benchmarking-cloud-storage-systems.git
    pip install "http://corelabs.coresecurity.com/index.php?module=Wiki&action=attachment&type=tool&page=Pcapy&file=pcapy-0.10.8.tar.gz"
    cd benchmarking-cloud-storage-systems
    pip install -r requirements.txt
    # you may want to start sniffing network traffic using tcpdump/wireshark/benchcloud.traffic.capturer before benchmarking:
    python -m benchcloud.benchcloud uploader -f benchcloud/example_benchmarking_conf/dropbox_random_upload_0.conf -a
