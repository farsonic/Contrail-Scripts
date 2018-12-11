#!/usr/bin/python
import sys, getopt
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from netaddr import *
from vnc_api import vnc_api


tenant_name = 'vCenter'
policy_name = raw_input('Name of Policy -> ')
policy_protocol = raw_input('Protocol (any/tcp/udp/icmp/icmp6) -> ')
policy_action = raw_input('Action (pass/deny) -> ')
source_network = raw_input('Source network name -> ')
if policy_protocol == "icmp":
    source_port = "-1"
else:
    source_port = raw_input('Source Port number -> ')
destination_network  = raw_input('Destination network name -> ')
if policy_protocol == 'icmp':
    destination_port = "-1"
else:
    destination_port = raw_input('Destination Port number -> ')
vnc = vnc_api.VncApi(username = "admin",password = "PASSWORD",tenant_name = "admin",api_server_host = "CONTRAIL_IP")
tenant = vnc.project_read(fq_name = ['default-domain', tenant_name])

#create policy
rule = vnc_api.PolicyRuleType(
        direction = '<>',
        protocol = policy_protocol,
        action_list = vnc_api.ActionListType(simple_action = policy_action),
        src_addresses = [vnc_api.AddressType(virtual_network = source_network)],
        src_ports = [vnc_api.PortType(start_port = source_port, end_port = source_port)],
        dst_addresses = [vnc_api.AddressType(virtual_network = destination_network)],
        dst_ports = [vnc_api.PortType(start_port = destination_port, end_port = destination_port)])

policy = vnc_api.NetworkPolicy(name = policy_name, parent_obj = tenant,
                network_policy_entries = vnc_api.PolicyEntriesType([rule]))
vnc.network_policy_create(policy)

#add the policy to each network
policy = vnc.network_policy_read(fq_name = ['default-domain', tenant_name, policy_name])
policy_type = vnc_api.VirtualNetworkPolicyType(sequence = vnc_api.SequenceType(major = 0, minor = 0))
vn = vnc.virtual_network_read(fq_name = ['default-domain', tenant_name, source_network])
vn.add_network_policy(ref_obj = policy, ref_data = policy_type)
vnc.virtual_network_update(vn)
vn = vnc.virtual_network_read(fq_name = ['default-domain', tenant_name, destination_network])
vn.add_network_policy(ref_obj = policy, ref_data = policy_type)
vnc.virtual_network_update(vn)
