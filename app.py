from flask import Flask
from prometheus_client import generate_latest, REGISTRY, Gauge
import subprocess
import re
import os

app = Flask(__name__)

# Prometheus Gauges with labels for client IPs
iperf3_jitter = Gauge('iperf3_jitter_ms', 'Jitter in milliseconds', ['client_ip', 'port'])
iperf3_packet_loss = Gauge('iperf3_packet_loss', 'Lost datagrams', ['client_ip', 'port'])
iperf3_total_datagrams = Gauge('iperf3_total_datagrams', 'Total datagrams', ['client_ip', 'port'])

def parse_iperf3_log(file_path, port):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    sessions_data = parse_iperf3_logs(lines)


    # Update Prometheus metrics
    for client_ip, session_data in sessions_data.items():
        # Since session_data['jitter_ms'], session_data['lost_datagrams'], and session_data['total_datagrams']
        # are lists, we need to decide how to aggregate or select the values (e.g., last value, max, average)
        # Here, we're using the last value of each list for simplicity.

        jitter = session_data['jitter_ms'][-1] if session_data['jitter_ms'] else 0
        lost = session_data['lost_datagrams'][-1] if session_data['lost_datagrams'] else 0
        total = session_data['total_datagrams'][-1] if session_data['total_datagrams'] else 0

        iperf3_jitter.labels(client_ip=client_ip, port=port).set(jitter)
        iperf3_packet_loss.labels(client_ip=client_ip, port=port).set(lost)
        iperf3_total_datagrams.labels(client_ip=client_ip, port=port).set(total)

def parse_iperf3_logs(lines):
    sessions_data = {}
    current_session_key = None

    for line in lines:
        # New session detection
        if "Accepted connection from" in line:
            ip_match = re.search(r"Accepted connection from ([\d\.]+),", line)
            if ip_match:
                client_ip = ip_match.group(1)
                current_session_key = client_ip  # Use IP as key; assuming unique sessions per IP for simplicity
                sessions_data[current_session_key] = {
                    "jitter_ms": [],
                    "lost_datagrams": [],
                    "total_datagrams": []
                }
        
        # Metrics collection
        if current_session_key:
            jitter_match = re.search(r"Jitter\s+([\d\.]+)\s+ms", line)
            lost_total_match = re.search(r"(\d+)/(\d+)\s+\(0%\)", line)  # Simplified to match given example
            if jitter_match:
                sessions_data[current_session_key]["jitter_ms"].append(float(jitter_match.group(1)))
            if lost_total_match:
                lost, total = lost_total_match.groups()
                sessions_data[current_session_key]["lost_datagrams"].append(int(lost))
                sessions_data[current_session_key]["total_datagrams"].append(int(total))

    return sessions_data


@app.route('/metrics')
def metrics():
    ports = [5201, 5202, 5203, 5204, 5205]
    for port in ports:
        log_file_path = f'/tmp/iperf3_{port}.log'
        if os.path.exists(log_file_path):
            parse_iperf3_log(log_file_path, str(port))
    return generate_latest(REGISTRY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
