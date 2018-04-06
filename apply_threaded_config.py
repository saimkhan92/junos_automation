# Script reads device(s) information from csv file, reads config (set format) from a file stored in current directory
# Applies config to devices uing threads

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from threading import Thread
import csv
import os
from subprocess import call
import time

def config_devices(row):
        set_commands_filename=row["skyent_hostname"]+".txt"
        print("Executing thread for "+row["skyent_hostname"]+" "+row["mgmt_ip"])
	response = os.system("ping -c 1 "+row["mgmt_ip"])
        while True:
                if response==0:
                        print("Device is up!!")
                        break
                else:
                        print(row["skyent_hostname"]+" device is down")
                        time.sleep(20)
			response = os.system("ping -c 1 "+row["mgmt_ip"])	
	max_tries=25
	while max_tries>0:
		try:
			
			with Device(host=row["mgmt_ip"], user="root", password="juniper1") as dev:
				fh=open(set_commands_filename,"r")
				set_commands_list=fh.read().splitlines()
				cu=Config(dev)
				for command in set_commands_list:
					if command:
						cu.load(command)

				if cu.commit():
					print("Configuration successfully commited")
					return True
				else:
					print("Error in committing config")	
					return False
		except:
			print("Waiting for netconf connection to be established. Tries left: "+str(max_tries))
			max_tries=max_tries-1
			time.sleep(10)
	print("Unable to establish netconf connection")
	return False
			
def main():
        dhcpd_restart_command="sudo /etc/init.d/isc-dhcp-server restart"
	dhcpd_return_code = call(dhcpd_restart_command, shell=True)
	print(dhcpd_return_code)
	csv_filename="host_to_mac_mapping.csv"
        device_data = csv.DictReader(open(csv_filename))
        for row in device_data:
                t = Thread(target=config_devices, args=(row,))
                t.start()

if __name__=="__main__":
        main()
