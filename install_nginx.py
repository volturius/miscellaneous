#!/usr/bin/python

import sys
import os
import subprocess
import fileinput
import re

def setup_repo():
	"""Sets up nginx yum package repository"""

	print "setting up nginx repository"
	yum_repo_file = '/etc/yum.repos.d/nginx.repo'
	yum_repo_data = '[nginx]\nname=nginx repo\nbaseurl=http://nginx.org/packages/centos/$releasever/$basearch/\ngpgcheck=0\nenabled=1'

	if os.path.exists(yum_repo_file):
		print "nginx package repo is already setup"
		return False
	else:
		f = open(yum_repo_file, 'w+')
		f.write(yum_repo_data)
		f.close()

		return True

def install_nginx():
	"""Installs nginx"""

	print "installing nginx"

	try:
		output = subprocess.Popen(['rpm', '-q', 'nginx'], stdout=subprocess.PIPE).communicate()[0]

	except OSError:
		print "problem running rpm"
		return False

	if output.startswith("nginx-"):
		print "nginx already installed!"
		return False

	try:
		subprocess.check_call(['yum', '-y', 'install', 'nginx'])

	except subprocess.CalledProcessError:
		print "nginx package installation failed"
		return False

	return True

def config_nginx(port):
	"""Configures nginx"""

	print "setting up nginx to run on port %s" % port
	conf_file = '/etc/nginx/conf.d/default.conf'
	old_string = 'listen       80;'
	new_string = 'listen       %s;' % port

	file = fileinput.input(conf_file, inplace=1)

	for line in file:
		print line.replace(old_string, new_string),

	file.close()


	return True

def start_nginx():
	"""Start nginx"""

	print "starting nginx"

	try:
		subprocess.check_call(['service', 'nginx', 'start'])

	except subprocess.CalledProcessError:
		print "nginx failed to start"
		return False

	except OSError:
		print "problem running service command"
		return False

	return True

def verify_nginx(port):
	"""Check nginx listening on correct port"""

	print "verifying nginx is installed and running"

	pattern = '^tcp.*:%s.*LISTEN\s+\d+/nginx\s*$' % port

	p = subprocess.Popen(["netstat", "-lnp"], stdout=subprocess.PIPE)
	stdout, stderr = p.communicate()
 
	for line in stdout.split('\n'):
		if re.search(pattern, line, flags=0):
			return True

	return False

def open_fw_port(port):
	"""Firewall is on by default.  Add rule to allow port 8080"""

	print "Poking firewall hole for port %s" % port

	try:
		subprocess.check_call([
			'iptables', '-I', 'INPUT', '1', 
			'-m', 'state', '--state', 'NEW', 
			'-m', 'tcp', '-p', 'tcp', 
			'--dport', port, '-j', 'ACCEPT'
			])

	except subprocess.CalledProcessError:
		print "problem installing firewall rule"
		return False

	try:
		subprocess.check_call([ 'service', 'iptables', 'save' ])

	except subprocess.CalledProcessError:
		print "problem saving firewall rules"
		return False

	return True

def get_exercise_content(dest, url):
	"""Fetches the index.html for this exercist"""

	print "Getting excercise web content"

	try:
		subprocess.check_call(['yum', '-y', 'install', 'wget'])

	except subprocess.CalledProcessError:
		print "wget package installation failed"
		return False


	try:
		subprocess.check_call([ 'wget', '-O', dest, url ])

	except subprocess.CalledProcessError:
		print "Failed to fetch exercise content"
		return False

	return True



nginx_port = '8080'

if not (setup_repo()):
	print "WARNING: Skipping repo setup"

if not (install_nginx()):
	print "ERROR: Problem installing nginx.  Exiting."
	sys.exit(1)

if not (config_nginx(nginx_port)):
	print "ERROR: Problem configuring nginx.  Exiting."
	sys.exit(1)

if not (start_nginx()):
	print "ERROR: Problem starting nginx.  Exiting."
	sys.exit(1)

if not (verify_nginx(nginx_port)):
	print "ERROR: nginx appears not to be running as expected.  Exiting."
	sys.exit(1)

if not (open_fw_port(nginx_port)):
	print "ERROR: Problem installing new firewall rule.  Exiting."
	sys.exit(1)

if not (get_exercise_content(
		'/usr/share/nginx/html/index.html', 
		'https://raw.github.com/puppetlabs/exercise-webpage/master/index.html'
		)):
	print "ERROR: Problem getting content.  Exiting."
	sys.exit(1)

print "Success: nginx installed and running"


