#!/usr/bin/env python

# This is a Linux command line tool to manage/start/stop VPN connections.
# It runs openvpn inside a "screen" window.
# Download the .ovpn files to the 'cfg' directory.
# It was made to use with KeepSolid VPN but could be used with any
# VPN provider for which you have OpenVPN configuration files.
# For convenience run through sudo or add openvpn to the sudoers file.

import os
import sys
import subprocess
import socket
import time

from collections import OrderedDict

cfgdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cfg')

def color(txt, mod=1, fg=32, bg=49):
	return "\033[%s;%d;%dm%s\033[0m" % (mod, fg, bg, txt)

def screen_running():
	directory = '/run/screen/S-%s' % getpass.getuser()
	listing = os.listdir(directory) if os.path.exists(directory) else []
	return listing[0] if len(listing) else False

def get_cmdline():
	with open('/run/openvpn.pid') as fp:
		return subprocess.check_output(['ps', '--no-headers', '-p', fp.read().strip(), '-o', 'args'])

def socket_commands(cmds):
	ret = []
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

	try:
		s.connect(('127.0.0.1', 60001))
		ret.append(s.recv(1024))

		for c in cmds:
			s.send('%s\n' % c)
			ret.append(s.recv(1024))

	except Exception as e:
		pass

	s.close()
	return ret

def stop():
	return socket_commands(['signal SIGTERM', 'quit'])

def start(idx):
	status = get_status()

	if status[0]:
		sys.exit("Error: VPN already connected. Disconnect first!")

	vpn_list = get_list()

	if idx in vpn_list:
		print "Status: Connecting..."

		cfgfile = os.path.join(cfgdir, vpn_list[idx])
		cmd = ['sudo', 'openvpn', '--writepid', '/run/openvpn.pid', '--management', '127.0.0.1', '60001', '--config', cfgfile]
		screen = screen_running()

		if not screen: # create new screen
			subprocess.call(['screen', '-d', '-m', '-t', 'OpenVPN'] + cmd)

		else: # create new window in existing screen
			subprocess.call(['screen', '-S', screen, '-x', '-X', 'screen', '-t', 'OpenVPN'] + cmd)

	else:
		print "Error: No such enpoint id"

def get_status():
	res = socket_commands(['state', 'quit'])

	if len(res) > 0:
		if 'CONNECTED' in res[1]:
			ret = res[1].split('\r')[0]
			cmdline = get_cmdline().split()
			ret += ',' + ','.join([str(_) for _ in cmdline])

			return (True, ret)

	return (False, 'Disconnected')

def print_status():
	status = get_status()

	if status[0]:
		status = status[1].split(',')
		state = status[1]
		int_ip = status[3]
		ext_ip = status[4]
		filename = ' '.join(status[15:])
		filename = filename[filename.rfind('/')+1:]
		filename = filename.replace('.ovpn', '')

		print 'Status: %s' % color(state, 1, 30, 102)
		print "Endpoint: %s" % filename
		print 'External IP: %s' % ext_ip

	else:
		print 'Status: %s' % color('DISCONNECTED', 1, 97, 41)

def get_list():

	ret = OrderedDict()

	vpns = []
	torrents = []
	streaming = []
	normal = []

	for f in os.listdir(cfgdir):
		if not f.endswith(".ovpn"):
			continue

		vpns.append(f)

	for v in sorted(vpns):
		if 'Torrents' in v:
			torrents.append(v)
		elif 'Streaming' in v:
			streaming.append(v)
		else:
			normal.append(v)

	cnt = 1
	for v in sorted(torrents):
		ret[cnt] = v
		cnt += 1
	for v in sorted(streaming):
		ret[cnt] = v
		cnt += 1
	for v in sorted(normal):
		ret[cnt] = v
		cnt += 1

	return ret

def view_list():

	vpns = get_list()
	for idx in vpns:
		print "%s: %s" % (color(idx), vpns[idx].replace('.ovpn', ''))


	###

if len(sys.argv) == 2 and sys.argv[1] == 'status':
	print_status()

elif len(sys.argv) == 2 and sys.argv[1] == 'list':
	view_list()

elif len(sys.argv) == 3 and sys.argv[1] == 'start':
	try:
		idx = int(sys.argv[2])
	except:
		sys.exit("Error: Invalid number")

	start(idx)

	while True:
		time.sleep(1)
		status = get_status()
		if status[0]:
			print_status()
			break

elif len(sys.argv) == 2 and sys.argv[1] == 'stop':
	stop()
	print_status()

elif len(sys.argv) == 2 and sys.argv[1] == 'ip':
	print 'External IP: %s' % subprocess.check_output(['dig', 'txt', 'o-o.myaddr.test.l.google.com', '@ns1.google.com', '+short']).strip()

else:

	print "%s ip           Fetch external IP address" % sys.argv[0]
	print "%s list         List available endpoints" % sys.argv[0]
	print "%s status       Show current VPN status" % sys.argv[0]
	print "%s start <nb>   Connect to endpoint number <nb>" % sys.argv[0]
	print "%s stop         Terminate active VPN connections" % sys.argv[0]

