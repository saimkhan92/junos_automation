from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.scp import SCP
from jnpr.junos.exception import ConfigLoadError
from lxml import etree
import logging
import time
import os

logging.basicConfig(level=logging.INFO)

with Device(host='10.10.10.11', user='root', password='Embe1mpls', mode='telnet', port='7026', gather_facts=True) as dev:
        # Step1: JDM load factory default and assign jmgmt0 in JDM an address via DHCP
        with Config(dev, mode='private') as cu:  
                try:
                        cu.load('delete interfaces jmgmt0', format='set')
                except ConfigLoadError:
                        print("@@@@@ jmgmt0 interface does not exist {}".format(ConfigLoadError))
                cu.load('set interfaces jmgmt0 unit 0 family inet dhcp', format='set')
                cu.load('set routing-options static route 0.0.0.0/0 next-hop 172.16.71.193', format='set')
                print("@@@@@ Setting DHCP on jmgmt0.0 and default static route\n")
                print("@@@@@ Comparing candidate configuration to the previously committed configuration\n")
                #cu.pdiff()
                cu.commit()
        # Step2: Pull DHCP assigned jmgmt0.0 management IP address
        data=dev.rpc.get_interface_information(interface_name='jmgmt0.0')
        output=data.xpath('///ifa-local[1]/text()')
        while not output:
                print("@@@@@ Waiting for management IP to be assigned by the DHCP server on the jmgmt0.0 interface")
                data=dev.rpc.get_interface_information(interface_name='jmgmt0.0')
                time.sleep(1)
                output=data.xpath('///ifa-local[1]/text()')
        mgmt_ip=output[0]
        print("@@@@@ Management address assigned to NFX is "+mgmt_ip )

try:
        with Device(host=mgmt_ip, user='root', password='Embe1mpls') as dev:
                print("@@@@@ Connected via SSH")
                print(dev.facts)
                with StartShell(dev) as ss:
                        print("@@@@@ Started shell")
                        ret, got=ss.run('cli')
                        print("@@@@@ Entering JCP")
                        ret, got=ss.run('ssh vjunos0')
                        ret, got=ss.run('juniper123') 
                        ret, got=ss.run('cli')
                        ret, got=ss.run('edit')
                        ret, got=ss.run('load factory-default')
                        ret, got=ss.run('set system root-authentication encrypted-password "$1$VcxSrvnL$KaNH2GcWOqnSOc7Fx7mIP0"')       #juniper123
                        ret, got=ss.run('commit and-quit')
                        ret, got=ss.run('exit')
                        ret, got=ss.run('exit')
                        print("@@@@@ Exiting JCP, entering JDM")
                        ret, got=ss.run('request setup jdm-auto-login vjunos0')
                        ret, got=ss.run('exit')
                        ret, got=ss.run('mv /etc/resolv.conf /etc/resolv.conf.backup')
                        ret, got=ss.run('echo "nameserver 8.8.8.8" >/etc/resolv.conf')
                        print("@@@@@ Transferring local shell script to the remote device")
                        with SCP(dev, progress=True) as scp1:
                                scp1.put("/root/ztp_dir/nfx_lfd/script_nfx.sh", remote_path="/var/tmp/")
                        print("@@@@@ Executing Shell Script on the remote device")
                        ret, got=ss.run('chmod 755 /var/tmp/script_nfx.sh')
                        ret, got=ss.run('/var/tmp/script_nfx.sh')
                        ret, got=ss.run('cli')
                        ret, got=ss.run('edit')
                        print("@@@@@ Entering JDM configuration mode "+got)
                        ret, got=ss.run('load factory-default')
                        ret, got=ss.run('set system root-authentication encrypted-password "$6$lQnPO$pGNh7LZJK/ZzJwsdGipgM3Mu3DjTsyQcT/BLUHCa2iM6R1lH6WweK58BakPoYoxorLfo29oTKuOFGoje0i0pc0"')
                        ret, got=ss.run('commit and-quit')
                        cu.load('set interfaces jmgmt0 unit 0 family inet dhcp', format='set')
                        cu.load('set routing-options static route 0.0.0.0/0 next-hop 172.16.71.193', format='set')
                        print("@@@@@ Hitting final commit")
                        ret, got=ss.run('commit and-quit')
except:
        print("@@@@@ End of script ")

with Device(host='10.10.10.11', user='root', password='Embe1mpls', mode='telnet', port='7026', gather_facts=True) as dev:
        with Config(dev, mode='private') as cu:
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
