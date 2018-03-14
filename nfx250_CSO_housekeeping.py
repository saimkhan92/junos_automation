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

def jcp_load_factory(mgmt_ip,host_name):
        try:
                with Device(host=mgmt_ip, user='root', password='Embe1mpls') as dev:
                        print("@@@@@ Connected via SSH")
                        print(dev.facts)
                        with StartShell(dev) as ss:
                                print("@@@@@ Started shell")
                                ret, got=ss.run('cli')
                                print("@@@@@ Entering JCP")
                                ret, got=ss.run('ssh vjunos0')
                                ret, got=ss.run('Embe1mpls')
                                ret, got=ss.run('cli')
                                ret, got=ss.run('edit')
                                ret, got=ss.run('load factory-default')
                                ret, got=ss.run('set system root-authentication encrypted-password "$1$mEqXYfsV$qjC0dBBp3DYD7sWOU5tN/1"')       #Embe1mpls
                                ret, got=ss.run('set protocols lldp interface all')
                                command='set system host-name '+host_name
                                ret, got=ss.run(command)
                                ret, got=ss.run('commit and-quit')
        except:
                print("@@@@@ Exception in JCP block ")
                return

def jdm_load_factory(mgmt_ip):
        try:
                with Device(host=mgmt_ip, user='root', password='Embe1mpls') as dev:
                        print("@@@@@ Connected via SSH")
                        print(dev.facts)
                        with StartShell(dev) as ss:
                                print("@@@@@ Started shell")
                                ret, got=ss.run('mv /etc/resolv.conf /etc/resolv.conf.backup')
                                ret, got=ss.run('echo "nameserver 8.8.8.8" >/etc/resolv.conf')
                                ret, got=ss.run('echo "172.16.76.174         dc76-regionalmsvm.juniper.net" >>/etc/hosts')
                                print("@@@@@ Transferring local shell script to the remote device")
                                with SCP(dev, progress=True) as scp1:
                                        scp1.put("/root/ztp_dir/nfx_lfd/files/script_nfx.sh", remote_path="/var/tmp/")
                                print("@@@@@ Executing Shell Script on the remote device")
                                ret, got=ss.run('chmod 755 /var/tmp/script_nfx.sh')
                                ret, got=ss.run('/var/tmp/script_nfx.sh')
                                ret, got=ss.run('cli')
                                ret, got=ss.run('edit')
                                print("@@@@@ Entering JDM configuration mode "+got)
                                ret, got=ss.run('load factory-default')
                                ret, got=ss.run('set system root-authentication encrypted-password "$6$lQnPO$pGNh7LZJK/ZzJwsdGipgM3Mu3DjTsyQcT/BLUHCa2iM6R1lH6WweK58BakPoYoxorLfo29oTKuOFGoje0i0pc0"')  #Embe1mpls
                                ret, got=ss.run('commit and-quit')
        except:
                print("@@@@@ Exception in JDM block ")

def set_mgmt_ip(telnet_ip,port):
        counter=0
        while counter<3:
                try:
                        with Device(host=telnet_ip, user='root', password='Embe1mpls', mode='telnet', port=port, gather_facts=True) as dev:
                                with Config(dev, mode='private') as cu:
                                        try:
                                                cu.load('delete interfaces jmgmt0', format='set')
                                        except ConfigLoadError:
                                                print("@@@@@ jmgmt0 interface does not exist {}".format(ConfigLoadError))
                                        cu.load('set interfaces jmgmt0 unit 0 family inet dhcp', format='set')
                                        cu.load('set routing-options static route 0.0.0.0/0 next-hop 172.16.71.193', format='set')
                                        print("@@@@@ Setting DHCP on jmgmt0.0 and default static route\n")
                                        cu.commit()
                                # testing jmgmt0.0 reachability
                                data=dev.rpc.get_interface_information(interface_name='jmgmt0.0')
                                output=data.xpath('///ifa-local[1]/text()')
                                while not output:
                                        print("@@@@@ Waiting for management IP to be assigned by the DHCP server on the jmgmt0.0 interface")
                                        data=dev.rpc.get_interface_information(interface_name='jmgmt0.0')
                                        time.sleep(1)
                                        output=data.xpath('///ifa-local[1]/text()')
                                mgmt_ip=output[0]
                                print("@@@@@ Your device is ready and the management IP is "+mgmt_ip )
                                return mgmt_ip
                except:
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
        csv_filename="/root/ztp_dir/nfx_lfd/files/console_addressing.csv"
        device_data = csv.DictReader(open(csv_filename))
        for row in device_data:
                if row["sn"]==sn:
                        telnet_ip=row["telnet_ip"]
                        port=row["port"]
                        host_name=row["device_name"]
                        print("Console server details (IP/Port): "+telnet_ip+" / "+port)
        mgmt_ip=set_mgmt_ip(telnet_ip,port)
        jdm_load_factory(mgmt_ip)
        mgmt_ip=set_mgmt_ip(telnet_ip,port)
        jcp_load_factory(mgmt_ip,host_name)
        mgmt_ip=set_mgmt_ip(telnet_ip,port)

if __name__ == "__main__":
        main()
