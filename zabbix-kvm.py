#!/usr/bin/env python3.6
import libvirt
import json
import sys
from optparse import OptionParser
import re
import xml.etree.ElementTree as ET

def main():
    options = parse_args()
    if options.item == "discovery":
        domain_list(options)
    elif options.item == "cpu":
        cpu(options)
    elif options.item == "mem":
        mem(options)
    elif options.item == "net_out":
        net_out(options)
    elif options.item == "net_in":
        net_in(options)
    elif options.item == "rd_bytes":
        rd_bytes(options)
    elif options.item == "wr_bytes":
        wr_bytes(options)

def parse_args():
    parser = OptionParser()
    valid_item = ["discovery", "cpu", "mem", "net_out", "net_in", "wr_bytes", "rd_bytes"]
    parser.add_option("", "--item", dest="item", help="", action="store", type="string", default=None)
    parser.add_option("", "--domain", dest="domain", help="", action="store", type="string", default=None)
    (options, args) = parser.parse_args()
    if options.item not in valid_item:
        parser.error("Item has to be one of: " + ", ".join(valid_item))
    return options

def kvm_connect():
    try:
        conn = libvirt.openReadOnly('qemu:///system')
    except:
        sys.stderr.write("There was an error connecting to the local libvirt daemon using 'qemu:///system'.")
        sys.exit(1)
    return conn

def extract_vnet_info(xml_desc):
    root = ET.fromstring(xml_desc)
    interface = root.find(".//interface[@type='bridge']")
    if interface is not None:
        target = interface.find("target")
        if target is not None:
            vnet = target.get('dev')
            bandwidth = interface.find("bandwidth")
            if bandwidth is not None:
                inbound = bandwidth.find("inbound")
                outbound = bandwidth.find("outbound")
                if inbound is not None and outbound is not None:
                    return vnet, int(inbound.get('average')), int(outbound.get('average'))
    return None, None, None
def domain_list(options):
    conn = kvm_connect()
    r = {"data": []}
    for domain in conn.listAllDomains(0):
        if domain.isActive():
            vnet, inbound, outbound = extract_vnet_info(domain.XMLDesc())
            if vnet:
                r["data"].append({
                    "{#DOMAINNAME}": domain.name(),
                    "{#DOMAINVNET}": vnet,
                    "{#INBOUND_LIMIT}": inbound,
                    "{#OUTBOUND_LIMIT}": outbound
                })
    print(json.dumps(r))

def cpu(options):
    conn = kvm_connect()
    domain = conn.lookupByName(options.domain)
    if not domain.isActive():
        print(0)
        return
    cpunum = domain.info()[3]
    cpuusertime = domain.info()[4]
    r = cpuusertime / cpunum / 10000000
    print(r)

def mem(options):
    conn = kvm_connect()
    domain = conn.lookupByName(options.domain)
    if not domain.isActive():
        print(0)
        return
    memstats = domain.memoryStats()
    r = (memstats["available"] - memstats["unused"]) / memstats["available"] * 100
    print(r)

def extract_vnet_name(xml_desc):
    import re
    match = re.search(r"<target dev='(vnet\d+)'", xml_desc)
    return match.group(1) if match else None

def net_out(options):
    conn = kvm_connect()
    domain = conn.lookupByName(options.domain)
    if not domain.isActive():
        print(0)
        return
    tapname = extract_vnet_name(domain.XMLDesc())
    if tapname:
        print(domain.interfaceStats(tapname)[4] * 8)
    else:
        print(0)

def net_in(options):
    conn = kvm_connect()
    domain = conn.lookupByName(options.domain)
    if not domain.isActive():
        print(0)
        return
    tapname = extract_vnet_name(domain.XMLDesc())
    if tapname:
        print(domain.interfaceStats(tapname)[0] * 8)
    else:
        print(0)

def rd_bytes(options):
    conn = kvm_connect()
    domain = conn.lookupByName(options.domain)
    if not domain.isActive():
        print(0)
        return
    r = domain.blockStatsFlags("vda")['rd_bytes']
    print(r)

def wr_bytes(options):
    conn = kvm_connect()
    domain = conn.lookupByName(options.domain)
    if not domain.isActive():
        print(0)
        return
    r = domain.blockStatsFlags("vda")['wr_bytes']
    print(r)

if __name__ == "__main__":
    main()
