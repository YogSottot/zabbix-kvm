referred from https://github.com/bushvin/zabbix-kvm-res

1. ```pip install libvirt-python``` or ```yum install python36-libvirt``` or ```apt install python3-libvirt```  
2. cp zabbix-kvm.py to /etc/zabbix/zabbix_agentd.d/scripts/zbx-kvm/
3. cp userparameter_zabbix-kvm.conf to /etc/zabbix/zabbix_agentd2.d/
4. import zabbix_kvm.yaml into zabbix frontend. I work in zabbix 7.0 (zabbix kvm.zml is old version without grpahs)

Template provides vps load graphs: cpu / ram / disk / network.  
The script no longer detects stopped domains. If a domain was stopped after getting into zabbix, then it will get null parameter values.  
The script does not need to be run via sudo.  
Data from the script is now output with the domain name instead of uuid. It seems to be more convenient to understand which virtual machine the graph belongs to.  
Tested in VMManager 5 on centos 7 with python3.6  
