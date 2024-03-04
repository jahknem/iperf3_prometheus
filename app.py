from flask import Flask, request, jsonify
from prometheus_client import generate_latest, REGISTRY, Gauge
import iperf3
import threading
import json
import os
import datetime

app = Flask(__name__)

# Define Prometheus Gauges
iperf3_bandwidth = Gauge('iperf3_bandwidth', 'Bandwidth measured by iperf3', ['port', 'sender_ip'])
iperf3_jitter = Gauge('iperf3_jitter', 'Jitter measured by iperf3', ['port', 'sender_ip'])
iperf3_packet_loss = Gauge('iperf3_packet_loss', 'Packet loss measured by iperf3', ['port', 'sender_ip',])

# Global structure to store test results
iperf3_results = {}

def iperf3_server_thread(port):
    try:
        server = iperf3.Server()
        server.port = port
        server.json_output = True
        print(f"Starting iperf3 server on port {port}")
        while True:
            try:
                result = server.run()
            except Exception as e:
                print(f"Failed to run iperf3 server on port {port}: {e}")
                continue
            print(f"Test result for port {port}: {result}")
            # Save dict as iperf3_port_date_time.json
            if not result.error:
                try:
                    result_data = result.json
                    sender_ip = result_data['start']['connected'][0]['remote_host']
                    bandwidth = result_data.get('end', {}).get('sum_received', {}).get('bits_per_second', 0)
                    jitter = result_data.get('end', {}).get('sum_received', {}).get('jitter_ms', 0)
                    packet_loss = result_data.get('end', {}).get('sum_received', {}).get('lost_percent', 0)
                    
                    # Use a combination of port, sender IP, and test ID as the unique key
                    result_key = (port, sender_ip)
                    iperf3_results[result_key] = {
                        'bandwidth': bandwidth,
                        'jitter': jitter,
                        'packet_loss': packet_loss,
                    }
                except Exception as e:
                    print(f"Failed to handle test result for port {port}: {e}")
    except Exception as e:
        print(f"Failed to start iperf3 server thread on port {port}: {e}")

@app.route('/metrics')
def metrics():
    global iperf3_results
    # Format the stored results for Prometheus
    for result_key, metrics in iperf3_results.items():
        port, sender_ip = result_key
        iperf3_bandwidth.labels(port=str(port), sender_ip=sender_ip).set(metrics['bandwidth'])
        iperf3_jitter.labels(port=str(port), sender_ip=sender_ip).set(metrics['jitter'])
        iperf3_packet_loss.labels(port=str(port), sender_ip=sender_ip).set(metrics['packet_loss'])

    # Clear the results after serving them
    iperf3_results.clear()
    return generate_latest(REGISTRY), 200


@app.route('/endpoint', methods=['POST'])
def endpoint():
    data = request.json
    # Process the data as needed
    return jsonify({"message": "Data received and processed"}), 200

if __name__ == '__main__':
    ports = [5201]  # Example ports
    for port in ports:
        try:
            print(f"Initializing iperf3 server on port {port}")
            threading.Thread(target=iperf3_server_thread, args=(port,)).start()
        except Exception as e:
            print(f"Failed to initialize iperf3 server on port {port}: {e}")

    app.run(host='0.0.0.0', port=5000)
