from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.scp import SCP
from jnpr.junos.exception import ConfigLoadError
from lxml import etree
import logging
import time
import os
from optparse import OptionParser
import csv
import sys
import re

def scp_rescue_config(mgmt_ip):
	try:
		with Device(host=mgmt_ip, user='root', password='Embe1mpls') as dev:
			with SCP(dev, progress=True) as scp1:
				print("@@@@@ Opening SCP connection")
				scp1.put("./rescue.conf.gz", remote_path="/config/")	# Specify correct path for rescue config file
	except:
		print("@@@@@ Error connecting to ge-0/0/0 IP. Manually set ge-0/0/0 IP, make sure it is reachable, try again.")

def get_mgmt_ip(telnet_ip,port):
	print("@@@@@ Calling function get_mgmt_ip")
        counter=0
        while counter<3:
                try:
                        with Device(host=telnet_ip, user='root', password='Embe1mpls', mode='telnet', port=port, gather_facts=True) as dev:
                                with Config(dev, mode='private') as cu:
                                        cu.load('set static route 0.0.0.0/0 next-hop 10.1.172.30', format='set')
                                        print("@@@@@ Setting default default static route\n")
                                        cu.commit()
				data=dev.rpc.get_interface_information(interface_name='ge-0/0/0.0')
                                output=data.xpath('///ifa-local[1]/text()')
                                while not output:
                                        print("@@@@@ Waiting for management IP to be assigned by the DHCP server on the jmgmt0.0 interface")
                                        data=dev.rpc.get_interface_information(interface_name='ge-0/0/0.0')
                                        time.sleep(1)
                                        output=data.xpath('///ifa-local[1]/text()')
                                mgmt_ip=output[0]
				mgmt_ip=mgmt_ip.strip()         # RPC returns an IP with a leading newline which needs to be stripped
                                print("@@@@@ Your device is ready and the management IP is "+mgmt_ip )
                                return mgmt_ip
                except:
                        counter+=1
                        print("@@@@@ Retrying connecting via console")
        print("@@@@@ Error in console connection\n@@@@@ Manually reconnect to the console, exit config/cli/shell, close connection, rerun script")
        sys.exit()

def load_rescue(telnet_ip,port):
	print("@@@@@ Calling function load_rescue")
        counter=0
        while counter<3:
                try:
                        with Device(host=telnet_ip, user='root', password='Embe1mpls', mode='telnet', port=port, gather_facts=True) as dev:
                                with Config(dev) as cu:
					reply=cu.rescue(action="reload")
					print(reply)
					if reply is not False:		
                                        	cu.commit()
						return True
					else:
						return False
			return
		except:																	# Specify the exact exception by name
                        counter+=1
                        print("@@@@@ Retrying connecting via console")
        print("@@@@@ Error in console connection\n@@@@@ Manually reconnect to the console, exit config/cli/shell, close connection, rerun script")
        sys.exit()

def main():
        logging.basicConfig(level=logging.INFO)
        parser = OptionParser(usage="usage: %prog [options]", version="%prog: version 1")
        parser.add_option("-s", "--serialnumber", dest="sn", default="1", help="Serial number of DC nodes as found in /root/ztp_dir/nfx_lfd/files/console_addressing.csv eg. -s 1")
	(options, args) = parser.parse_args()
        sn=options.sn
        print(sn)
        csv_filename="console_addressing.csv"
        device_data = csv.DictReader(open(csv_filename))
        for row in device_data:
                if row["sn"]==sn:
                        telnet_ip=row["telnet_ip"]
                        port=row["port"]
                        host_name=row["device_name"]
                        print("Console server details (IP/Port): "+telnet_ip+" / "+port)
	success=load_rescue(telnet_ip,port)
	if success:
		print("Successfully reloaded the base config")
		print("SUCCESS: "+ str(success))
		sys.exit()
	else:
		mgmt_ip=get_mgmt_ip(telnet_ip,port)
		scp_rescue_config(mgmt_ip)
	success=load_rescue(telnet_ip,port)
	print("Successfully reloaded the base config")
	print("SUCCESS: "+ str(success))

if __name__ == "__main__":
        main()
