from flask import Flask, render_template, request,jsonify
import subprocess
import paramiko
import socket

app = Flask(__name__)

# SSH connection details
ssh_username = 'username'
ssh_password = 'password'
ssh_port = 22
ssh = None
ip_address = 'ip_address'


def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip_address, username=ssh_username, password=ssh_password)
    except (paramiko.ssh_exception.AuthenticationException, socket.error) as e:
        print('Error: ', e)
    else:
        return ssh

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getMac', methods=['GET'])
def get_mac_address():
    cmd = f"arp -a {ip_address}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout.split('\n')
    mac_address = ""
    for line in output:
        if ip_address in line:
            mac_address = line.split()[1].replace('-', ':')
            break
    return render_template("index.html", mac_address=mac_address)


@app.route('/getRam', methods=['GET'])
def get_ram_infos():
    ssh = get_ssh()
     # Execute the `free` command on the remote device
    stdin, stdout, stderr = ssh.exec_command('free -h')

    # Parse the output of the `free` command
    mem_info = stdout.read().decode('utf-8').split()[7:10]
    total_mem, used_mem, free_mem = mem_info
    return render_template("index.html", total_mem=total_mem,used_mem=used_mem,
                        free_mem=free_mem)

@app.route('/getTempCpu')
def get_temp_cpu():
    ssh = get_ssh()
     # Execute the `free` command on the remote device
    stdin, stdout, stderr = ssh.exec_command('sensors')
    output = stdout.read().decode('utf-8')
    
    # Parse the output of the `sensors` command
    for line in output.split('\n'):
        if line.startswith('Core 0:'):
            temperature = line.split()[2][1:]
            return render_template("index.html", temperature=temperature)
    return "<h1>Not possible</h1>"


if __name__ == '__main__':
    app.run(debug=True)
