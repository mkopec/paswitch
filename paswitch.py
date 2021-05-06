#!/bin/python
import pulsectl
import subprocess
import argparse

parser = argparse.ArgumentParser(description='PulseAudio sink switcher')
parser.add_argument('--menu', nargs=1, default=['bemenu'], required=False)
args = parser.parse_args()
menu = args.menu[0] + ' -p "pulseaudio"'

with pulsectl.Pulse('sink-switcher') as pulse:
	index = 0
	activeindex = 0
	sinks={}

	for sink in pulse.sink_list():
		if 'alsa.card_name' in sink.proplist:
			key = sink.proplist.get('alsa.card_name') + " " + sink.proplist.get('alsa.name')
		else:
			key = sink.proplist.get('device.description')
		sinks[key] = sink
		
		if sink.proplist.get('node.name') == pulse.server_info().default_sink_name:
			activeindex = index
		index = index + 1

	menu = menu + " -I " + str(activeindex)

	command=''
	for key in sinks.keys():
		command = command + key + '\n'
	
	p = subprocess.Popen(menu,
						stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	
	stdout, stderr = p.communicate(input=bytes(command, 'utf-8'))
	selection = sinks.get(stdout.decode('utf-8').replace('\n', ''))
	pulse.default_set(selection)
