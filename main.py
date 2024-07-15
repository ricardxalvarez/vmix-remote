from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Store the current vMix IPs and ports, identified by unique IDs
vmix_servers = {}

# Endpoint to update vMix IP and port for a specific server
@app.route('/update_vmix', methods=['POST'])
def update_vmix():
    data = request.get_json()
    vmix_id = data.get('id')
    vmix_ip = data.get('ip')
    vmix_port = data.get('port')
    print(vmix_servers)
    if not vmix_id or not vmix_ip or not vmix_port:
        return jsonify({"status": "error", "message": "ID, IP, and port are required"}), 400

    vmix_servers[vmix_id] = {"ip": vmix_ip, "port": vmix_port}
    return jsonify({"status": "success", "message": "vMix server updated"})

# Function to send a command to a specific vMix server
def send_command(vmix_id, function, input=None, value=None, duration=None, source=None):
    vmix_server = vmix_servers.get(vmix_id)
    if not vmix_server:
        return {"status": "error", "message": f"vMix server with ID {vmix_id} not found"}

    vmix_ip_address = vmix_server['ip']
    vmix_port = vmix_server['port']
    vmix_url = f"http://{vmix_ip_address}:{vmix_port}/api"
    params = {'Function': function}
    if input is not None:
        params['Input'] = input
    if value is not None:
        params['Value'] = value
    if duration is not None:
        params['Duration'] = duration
    if source is not None:
        params['MIX'] = source
    response = requests.get(vmix_url, params=params)
    print(response)
    if response.status_code == 200:
        return {"status": "success", "message": "Command executed successfully"}
    else:
        return {"status": "error", "message": f"Failed to send command. Status code: {response.status_code}"}

# Function to check if a specific vMix server is running
def check_vmix_status(vmix_id):
    vmix_server = vmix_servers.get(vmix_id)
    if not vmix_server:
        return {"status": "error", "message": f"vMix server with ID {vmix_id} not found"}

    vmix_ip_address = vmix_server['ip']
    vmix_port = vmix_server['port']
    vmix_url = f"http://{vmix_ip_address}:{vmix_port}/api"
    try:
        response = requests.get(vmix_url)
        if response.status_code == 200:
            return {"status": "success", "message": "vMix server is running"}
        else:
            return {"status": "error", "message": f"vMix server responded with status code {response.status_code}"}
    except requests.ConnectionError:
        return {"status": "error", "message": "Failed to connect to vMix server"}

# Endpoint to send a command to a specific vMix server
@app.route('/send_command', methods=['POST'])
def handle_send_command():
    data = request.get_json()
    vmix_id = data.get('id')
    function = data.get('function')
    input = data.get('input')
    value = data.get('value')
    duration = data.get('duration')
    source = data.get('source')
    if not vmix_id or not function:
        return jsonify({"status": "error", "message": "ID and function are required"}), 400

    result = send_command(vmix_id, function, input, value, duration)
    return jsonify(result)

# Endpoint to check if a specific vMix server is running
@app.route('/check_vmix_status', methods=['GET'])
def handle_check_vmix_status():
    vmix_id = request.args.get('id')
    if not vmix_id:
        return jsonify({"status": "error", "message": "ID is required"}), 400

    result = check_vmix_status(vmix_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
