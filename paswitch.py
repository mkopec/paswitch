#!/bin/python
import pulsectl
import subprocess
import argparse

# CLI argument parsing
parser = argparse.ArgumentParser(description='PulseAudio sink switcher')
parser.add_argument('--menu','-m', nargs=1, default=['bemenu'], required=False)
parser.add_argument('--prompt','-p', nargs=1, default=['pulseaudio'], required=False)
args = parser.parse_args()
menu = args.menu[0] + ' -p ' + args.prompt[0]

with pulsectl.Pulse('sink-switcher') as pulse:
	index = 0 # Used for determining the current default sink
	activeindex = 0
	sinks = {}

	for sink in pulse.sink_list():
		key = sink.proplist.get('device.description')
		sinks[key] = sink
		
		if sink.proplist.get('node.name') == pulse.server_info().default_sink_name:
			activeindex = index
		index = index + 1

	menu = menu + " -I " + str(activeindex)

	options = '' # List of options to be passed to bemenu
	for key in sinks.keys():
		options = options + key + '\n'

	# Launch bemenu subprocess	
	p = subprocess.Popen(menu, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	
	stdout, stderr = p.communicate(input=bytes(options, 'utf-8')) # Pass options to bemenu
	p.wait()
	
	if p.returncode != -1:
		selection = sinks.get(stdout.decode('utf-8').replace('\n', '')) # Retrieve sink that matches selection from bemenu
		pulse.default_set(selection)
