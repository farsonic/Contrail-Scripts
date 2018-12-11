#!/usr/bin/python
import sys, getopt
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from netaddr import *
from vnc_api import vnc_api

AS='65000'
network_number=1
ip = IPNetwork('172.24.0.0/8')
subnets = list(ip.subnet(24))
vnc = vnc_api.VncApi(username = "admin",password = "contrail123",tenant_name = "admin",api_server_host = "192.168.101.200")
tenant = vnc.project_read(fq_name = ['default-domain', 'vCenter'])
ipam = vnc.network_ipam_read(fq_name = ['default-domain', 'vCenter', 'vCenter-ipam'])


for subnet in subnets:
    start_addr = str(subnet[10])
    end_addr = str(subnet[100])
    vn = vnc_api.VirtualNetwork(name = "Customer_"+str(network_number), parent_obj = tenant)
    cidr = str(subnet)
    print subnet,"RD",str(AS)+":"+str(network_number)
    prefix, prefix_len = cidr.split('/')
    subnet = vnc_api.SubnetType(ip_prefix = prefix, ip_prefix_len = prefix_len)
    alloc_pools = []
    alloc_pools.append(vnc_api.AllocationPoolType(start=start_addr,end=end_addr))
    ipam_subnet = vnc_api.IpamSubnetType(subnet = subnet,advertise_default=True,allocation_pools=alloc_pools)
    vn.set_network_ipam(ref_obj = ipam, ref_data = vnc_api.VnSubnetsType([ipam_subnet]))
    route_targets = vnc_api.RouteTargetList(['target:' +str(AS)+":"+str(network_number)])
    vn.set_route_target_list(route_targets)
    vnc.virtual_network_create(vn)
    network_number = network_number+1
