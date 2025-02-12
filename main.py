from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Stores the vMix servers
vmix_servers = {}

@app.route('/', methods=['GET'])
def main():
    return 'Welcome!!'

@app.route('/update_vmix', methods=['POST'])
def update_vmix():
    data = request.get_json()
    vmix_id = data.get('id')
    vmix_ip = data.get('ip')
    vmix_port = data.get('port')

    if not vmix_id or not vmix_ip or not vmix_port:
        return jsonify({"status": "error", "message": "ID, IP, and port are required"}), 400

    # Updates or creates a new server
    vmix_servers[vmix_id] = {"id": vmix_id, "ip": vmix_ip, "port": vmix_port}
    return jsonify({"status": "success", "message": "vMix server updated"})


def send_command(vmix_id, function, input=None, value=None, duration=None, source=None):
    vmix_server = vmix_servers.get(vmix_id)
    if not vmix_server:
        return {"status": "error", "message": f"vMix server ID {vmix_id} not found"}

    vmix_url = f"http://{vmix_server['ip']}:{vmix_server['port']}/api"
    params = {'Function': function}
    if input: params['Input'] = input
    if value: params['Value'] = value
    if duration: params['Duration'] = duration
    if source: params['MIX'] = source

    try:
        response = requests.get(vmix_url, params=params)
        if response.status_code == 200:
            return {"status": "success", "message": "Command executed successfully"}
        else:
            return {"status": "error", "message": f"Error executing command. Code {response.status_code}"}
    except requests.ConnectionError:
        return {"status": "error", "message": "Connection error with vMix server"}


def assign_vmix_state(vmix_id, state, source):
    vmix_server = vmix_servers.get(vmix_id)
    if not vmix_server:
        return {"status": "error", "message": f"vMix server ID {vmix_id} not found"}

    # Initiates the states list if it doesn't exist
    if "states" not in vmix_server:
        vmix_server["states"] = []
    vmix_server["states"] = [s for s in vmix_server["states"] if s["state"] != state]  # Remueve estados previos
    vmix_server["states"].append({"state": state, "source": source})

    return {"status": "success", "message": "State updated"}


def change_vmix_state(vmix_id, state):
    vmix_server = vmix_servers.get(vmix_id)
    if not vmix_server or "states" not in vmix_server:
        return {"status": "error", "message": f"vMix server ID {vmix_id} not found or no states assigned"}

    vmix_state = next((s for s in vmix_server["states"] if s["state"] == state), None)
    if not vmix_state:
        return {"status": "error", "message": f"State {state} not found"}

    return send_command(vmix_id, 'Cut', source=vmix_state['source'])


@app.route('/send_command', methods=['POST'])
def handle_send_command():
    data = request.get_json()
    vmix_id = data.get('id')
    function = data.get('function')

    if not vmix_id or not function:
        return jsonify({"status": "error", "message": "ID and function are required"}), 400

    result = send_command(vmix_id, function, data.get('input'), data.get('value'), data.get('duration'), data.get('source'))
    return jsonify(result)


@app.route('/check_vmix_status', methods=['GET'])
def handle_check_vmix_status():
    vmix_id = request.args.get('id')
    if not vmix_id:
        return jsonify({"status": "error", "message": "ID required"}), 400

    vmix_server = vmix_servers.get(vmix_id)
    if not vmix_server:
        return jsonify({"status": "error", "message": f"vMix server ID {vmix_id} not found"})

    vmix_url = f"http://{vmix_server['ip']}:{vmix_server['port']}/api"
    try:
        response = requests.get(vmix_url)
        return jsonify({"status": "success" if response.status_code == 200 else "error", 
                        "message": "Server online" if response.status_code == 200 else f"Error {response.status_code}"})
    except requests.ConnectionError:
        return jsonify({"status": "error", "message": "Could not connect to vmix server"})


@app.route('/assign_source_state', methods=['POST'])
def assign_state():
    data = request.get_json()
    vmix_id = data.get('id')
    source = data.get('source')
    state = data.get('state')

    if not vmix_id or not source or not state:
        return jsonify({"status": "error", "message": "ID, source and required"}), 400

    result = assign_vmix_state(vmix_id, state, source)
    return jsonify(result)


@app.route('/change_state', methods=['POST'])
def change_state():
    data = request.get_json()
    vmix_id = data.get('id')
    state = data.get('state')

    if not vmix_id or not state:
        return jsonify({"status": "error", "message": "ID and state required"}), 400

    result = change_vmix_state(vmix_id, state)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)