from flask import Flask, render_template, redirect, url_for, request
import sql 
import paramiko
import subprocess

app = Flask(__name__)

def list_log_files(username, password):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('archsurfer', username=username, password=password, timeout=5)
		_, stdout, _ = ssh.exec_command("ls -t /home/admin/server/logs")
		log_files = stdout.read().decode().split()
		ssh.close()
		return log_files
	except Exception as e:
		print("Error listing log files:", e)
		return []

def get_log_files(username, password):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('archsurfer', username=username, password=password, timeout=5)
		
		# Liste der Log-Dateien abrufen
		_, stdout, _ = ssh.exec_command("ls /home/admin/server/logs")
		log_files = stdout.read().decode().split()

		log_contents = {}
		for log_file in log_files:
			if log_file.endswith('.log.gz'):
				command = f"zcat /home/admin/server/logs/{log_file}"
				_, stdout, _ = ssh.exec_command(command)
				log_contents[log_file] = stdout.read().decode()
			elif log_file.endswith('.log'):
				command = f"cat /home/admin/server/logs/{log_file}"
				_, stdout, _ = ssh.exec_command(command)
				log_contents[log_file] = stdout.read().decode()

		ssh.close()
		return log_contents
	except Exception as e:
		print("Error getting log files:", e)
		return {}

def get_server_status(username, password):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('archsurfer', username=username, password=password, timeout=5)
		ssh.close()
		return True
	except Exception as e:
		return False

def send_wol(mac_address):
	try:
		subprocess.call(["wakeonlan", mac_address])
		return True
	except Exception as e:
		print("WoL error:", e)
		return False

def check_ssh_connection(username, password):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('archsurfer', username=username, password=password, timeout=5)
		ssh.close()
		return True
	except Exception as e:
		print("SSH connection error:", e)
		return False

def execute_ssh_command(command):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('archsurfer', username=username, password=password, timeout=5)
		stdin, stdout, stderr = ssh.exec_command(command)
		output = stdout.read().decode()
		error = stderr.read().decode()
		ssh.close()
		return output, error
	except Exception as e:
		print("SSH command execution error:", e)
		return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		global username, password
		username = request.form.get('username')
		password = request.form.get('password')
		return redirect(url_for('dashboard', username=username, password=password))
	return render_template('index.html')

@app.route('/dashboard')
def dashboard():
	if not sql.check_user(username, password):
		return redirect(url_for('index'))

	server_status = get_server_status(username, password)

	commands = [
		"uname -a",  # Display system information
		"uptime",    # Show uptime
		"df -h",     # Display disk space
		"free -m",   # Show memory usage
	]

	if server_status:
		command_results = {}
		for command in commands:
			output, error = execute_ssh_command(command)
			if error:
				command_results[command] = f"Error: {error}"
			else:
				command_results[command] = output
	else:
		command_results = {}
		for command in commands:
			command_results[command] = "Server is OFF"

	return render_template('dashboard.html', command_results=command_results, server_status=server_status)

@app.route('/delete_log', methods=['POST'])
def delete_log():
	if not sql.check_user(username, password):
		return redirect(url_for('index'))
	log_file = request.form.get('current_log_file')
	command = f"rm /home/admin/server/logs/{log_file}"
	execute_ssh_command(command)
	return redirect(url_for('logs'))

@app.route('/start_server', methods=['POST'])
def start_server():
	mac_address = "10:e7:c6:31:62:dc"
	send_wol(mac_address)
	while not get_server_status(username, password):
		pass
	return redirect(url_for('dashboard'))

@app.route('/stop_server', methods=['POST'])
def stop_server():
	command = f'sudo -S shutdown -P now <<< "{password}"'
	execute_ssh_command(command)
	while get_server_status(username, password):
		pass
	return redirect(url_for('dashboard'))

@app.route('/restart_server', methods=['POST'])
def restart_server():
	command = f"sudo -S reboot <<< '{password}'"
	execute_ssh_command(command)
	while get_server_status(username, password):
		pass
	while not get_server_status(username, password):
		pass
	return redirect(url_for('dashboard'))

@app.route('/logs')
def logs():
	if not sql.check_user(username, password):
		return redirect(url_for('index'))
	log_files = list_log_files(username, password)
	log_contents = get_log_files(username, password)
	return render_template('logs.html', log_files=log_files, log_contents=log_contents)

if __name__ == '__main__':
	sql.generate_db()
	sql.add_user('admin', 'cx')
	app.run(debug=True)
