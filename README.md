docker build . -t jahknem/iperf3_server_exporter
docker run -p 5000:5000 jahknem/iperf3_server_exporter