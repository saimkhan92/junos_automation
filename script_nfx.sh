# Consumed by nfx250_CSO_housekeeping.py

cp /var/phone-home/phcd_dhcp_server_cfg.xml /var/phone-home/phcd_dhcp_server_cfg.xml.ORIGINAL
{ rm /var/phone-home/phcd_dhcp_server_cfg.xml && awk '{gsub("10.10.10", "4.4.4", $0); print}' > /var/phone-home/phcd_dhcp_server_cfg.xml; } < /var/phone-home/phcd_dhcp_server_cfg.xml
cp /var/phone-home/phcd_isc_dhcpd.conf /var/phone-home/phcd_isc_dhcpd.conf.ORIGINAL
{ rm /var/phone-home/phcd_isc_dhcpd.conf && awk '{gsub("10.10.10", "4.4.4", $0); print}' > /var/phone-home/phcd_isc_dhcpd.conf; } < /var/phone-home/phcd_isc_dhcpd.conf
cp /var/phone-home/phcd_setup.sh /var/phone-home/phcd_setup.sh.ORIGINAL
{ rm /var/phone-home/phcd_setup.sh && awk '{gsub("10.10.10", "4.4.4", $0); print}' > /var/phone-home/phcd_setup.sh; } < /var/phone-home/phcd_setup.sh
sed -i 's/net.ipv4.conf.default.rp_filter=1/net.ipv4.conf.default.rp_filter=0/g' /etc/sysctl.conf
sed -i 's/net.ipv4.conf.all.rp_filter=1/net.ipv4.conf.all.rp_filter=0/g' /etc/sysctl.conf
sed -i '/net.ipv4.conf.all.rp_filter=0/a\net.ipv6.conf.default.accept_ra=0' /etc/sysctl.conf
sed -i '/net.ipv4.conf.all.rp_filter=0/a\net.ipv6.conf.all.accept_ra=0' /etc/sysctl.conf
sed -i '/net.ipv4.conf.all.rp_filter=0/a\net.ipv4.conf.jsxe0/0.rp_filter=0' /etc/sysctl.conf
sed -i '/net.ipv4.conf.all.rp_filter=0/a\net.ipv4.conf.jsxe0/1.rp_filter=0' /etc/sysctl.conf
sed -i '/net.ipv4.conf.all.rp_filter=0/a\net.ipv4.conf.jsxe0/2.rp_filter=0' /etc/sysctl.conf
