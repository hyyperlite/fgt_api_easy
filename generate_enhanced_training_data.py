#!/usr/bin/env python3
"""
Enhanced Training Data Generator for FortiGate API Client ML/AI Components

This script generates comprehensive, diverse training data for the ML/AI models
to improve classification accuracy and handling of various FortiGate API endpoints.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os


class EnhancedTrainingDataGenerator:
    """
    Generates diverse, realistic training data for FortiGate API endpoints
    """
    
    def __init__(self):
        self.categories = {
            'firewall_policy': 'Firewall policy configuration and rules',
            'firewall_objects': 'Firewall objects like addresses, services, groups',
            'routing': 'Routing tables, static routes, BGP, OSPF',
            'system': 'System configuration, interfaces, global settings',
            'vpn': 'VPN configuration, IPSec, SSL VPN',
            'monitor': 'Monitoring data, logs, status information',
            'user_auth': 'User authentication, LDAP, local users',
            'security_profiles': 'AV, IPS, DLP, Application Control profiles',
            'wireless': 'WiFi configuration, access points, SSIDs',
            'switching': 'Switch configuration, VLANs, ports',
            'log_analytics': 'Log analysis, traffic reports, security events'
        }
        
        # Comprehensive endpoint patterns
        self.endpoint_patterns = {
            'firewall_policy': [
                '/cmdb/firewall/policy',
                '/cmdb/firewall/policy6',
                '/cmdb/firewall/local-in-policy',
                '/cmdb/firewall/local-in-policy6',
                '/cmdb/firewall/central-snat-map',
                '/cmdb/firewall/proxy-policy',
                '/cmdb/firewall/multicast-policy',
                '/cmdb/firewall/multicast-policy6'
            ],
            'firewall_objects': [
                '/cmdb/firewall/address',
                '/cmdb/firewall/address6',
                '/cmdb/firewall/addrgrp',
                '/cmdb/firewall/addrgrp6',
                '/cmdb/firewall/service/custom',
                '/cmdb/firewall/service/group',
                '/cmdb/firewall/schedule/recurring',
                '/cmdb/firewall/schedule/onetime',
                '/cmdb/firewall/vip',
                '/cmdb/firewall/vipgrp',
                '/cmdb/firewall/internet-service-name',
                '/cmdb/firewall/internet-service-group'
            ],
            'routing': [
                '/cmdb/router/static',
                '/cmdb/router/static6',
                '/cmdb/router/policy',
                '/cmdb/router/route-map',
                '/cmdb/router/prefix-list',
                '/cmdb/router/access-list',
                '/cmdb/router/bgp',
                '/cmdb/router/ospf',
                '/cmdb/router/rip',
                '/monitor/router/ipv4',
                '/monitor/router/ipv6'
            ],
            'system': [
                '/cmdb/system/global',
                '/cmdb/system/interface',
                '/cmdb/system/zone',
                '/cmdb/system/admin',
                '/cmdb/system/ha',
                '/cmdb/system/dns',
                '/cmdb/system/fortiguard',
                '/cmdb/system/ntp',
                '/cmdb/system/snmp/community',
                '/monitor/system/status',
                '/monitor/system/performance',
                '/monitor/system/interface'
            ],
            'vpn': [
                '/cmdb/vpn/ipsec/phase1',
                '/cmdb/vpn/ipsec/phase1-interface',
                '/cmdb/vpn/ipsec/phase2',
                '/cmdb/vpn/ipsec/phase2-interface',
                '/cmdb/vpn/ssl/settings',
                '/cmdb/vpn/ssl/web/portal',
                '/cmdb/vpn/certificate/local',
                '/cmdb/vpn/certificate/ca',
                '/monitor/vpn/ipsec',
                '/monitor/vpn/ssl'
            ],
            'monitor': [
                '/monitor/system/status',
                '/monitor/system/ha-statistics',
                '/monitor/system/performance',
                '/monitor/system/available-interfaces',
                '/monitor/firewall/session',
                '/monitor/firewall/policy',
                '/monitor/log/current-disk-usage',
                '/monitor/user/firewall',
                '/monitor/wifi/client',
                '/monitor/switch/managed-switch'
            ],
            'user_auth': [
                '/cmdb/user/local',
                '/cmdb/user/group',
                '/cmdb/user/ldap',
                '/cmdb/user/radius',
                '/cmdb/user/tacacs+',
                '/cmdb/user/peer',
                '/cmdb/user/peergrp',
                '/monitor/user/firewall'
            ],
            'security_profiles': [
                '/cmdb/antivirus/profile',
                '/cmdb/ips/sensor',
                '/cmdb/application/list',
                '/cmdb/dlp/sensor',
                '/cmdb/webfilter/profile',
                '/cmdb/dnsfilter/profile',
                '/cmdb/icap/profile',
                '/cmdb/waf/profile',
                '/cmdb/voip/profile'
            ],
            'wireless': [
                '/cmdb/wireless-controller/wtp',
                '/cmdb/wireless-controller/wtp-profile',
                '/cmdb/wireless-controller/vap',
                '/cmdb/wireless-controller/setting',
                '/monitor/wifi/client',
                '/monitor/wifi/ap_status'
            ],
            'switching': [
                '/cmdb/switch-controller/managed-switch',
                '/cmdb/switch-controller/switch-profile',
                '/cmdb/switch-controller/vlan',
                '/cmdb/system/virtual-switch',
                '/monitor/switch/managed-switch'
            ],
            'log_analytics': [
                '/monitor/log/device',
                '/api/v2/monitor/log/fortiguard',
                '/api/v2/monitor/log/virus',
                '/api/v2/monitor/log/webfilter',
                '/api/v2/monitor/log/ips',
                '/api/v2/monitor/log/app-ctrl'
            ]
        }
        
    def generate_firewall_policy_data(self) -> List[Dict[str, Any]]:
        """Generate diverse firewall policy training data"""
        policies = []
        
        # Basic allow policies
        allow_policies = [
            {
                'policyid': 1, 'name': 'Allow_Web_Traffic', 'srcintf': [{'name': 'internal'}],
                'dstintf': [{'name': 'wan1'}], 'srcaddr': [{'name': 'internal_subnet'}],
                'dstaddr': [{'name': 'all'}], 'service': [{'name': 'HTTP'}, {'name': 'HTTPS'}],
                'action': 'accept', 'status': 'enable', 'logtraffic': 'all'
            },
            {
                'policyid': 2, 'name': 'Allow_Email_Servers', 'srcintf': [{'name': 'internal'}],
                'dstintf': [{'name': 'dmz'}], 'srcaddr': [{'name': 'internal_users'}],
                'dstaddr': [{'name': 'mail_servers'}], 'service': [{'name': 'SMTP'}, {'name': 'IMAP'}],
                'action': 'accept', 'status': 'enable', 'nat': 'enable'
            },
            {
                'policyid': 3, 'name': 'Allow_VPN_Access', 'srcintf': [{'name': 'ssl.root'}],
                'dstintf': [{'name': 'internal'}], 'srcaddr': [{'name': 'SSLVPN_TUNNEL_ADDR1'}],
                'dstaddr': [{'name': 'internal_servers'}], 'service': [{'name': 'ALL'}],
                'action': 'accept', 'status': 'enable', 'groups': [{'name': 'VPN_Users'}]
            }
        ]
        
        # Deny policies
        deny_policies = [
            {
                'policyid': 10, 'name': 'Block_Social_Media', 'srcintf': [{'name': 'internal'}],
                'dstintf': [{'name': 'wan1'}], 'srcaddr': [{'name': 'restricted_users'}],
                'dstaddr': [{'name': 'social_media_sites'}], 'service': [{'name': 'HTTP'}, {'name': 'HTTPS'}],
                'action': 'deny', 'status': 'enable', 'logtraffic': 'all'
            },
            {
                'policyid': 11, 'name': 'Block_P2P_Traffic', 'srcintf': [{'name': 'internal'}],
                'dstintf': [{'name': 'wan1'}], 'srcaddr': [{'name': 'all'}],
                'dstaddr': [{'name': 'all'}], 'service': [{'name': 'P2P_Services'}],
                'action': 'deny', 'status': 'enable', 'schedule': 'business_hours'
            }
        ]
        
        # Security profile policies
        security_policies = [
            {
                'policyid': 20, 'name': 'Web_Security_Policy', 'srcintf': [{'name': 'internal'}],
                'dstintf': [{'name': 'wan1'}], 'srcaddr': [{'name': 'all'}],
                'dstaddr': [{'name': 'all'}], 'service': [{'name': 'HTTP'}, {'name': 'HTTPS'}],
                'action': 'accept', 'status': 'enable', 'utm-status': 'enable',
                'av-profile': 'default', 'ips-sensor': 'high_security',
                'application-list': 'block_high_risk', 'webfilter-profile': 'strict'
            }
        ]
        
        all_policies = allow_policies + deny_policies + security_policies
        
        for policy in all_policies:
            for endpoint in self.endpoint_patterns['firewall_policy'][:3]:  # Use first 3 endpoints
                policies.append({
                    'endpoint': endpoint,
                    'data': policy,
                    'category': 'firewall_policy'
                })
        
        return policies
    
    def generate_firewall_objects_data(self) -> List[Dict[str, Any]]:
        """Generate diverse firewall objects training data"""
        objects_data = []
        
        # Address objects
        addresses = [
            {'name': 'internal_subnet', 'type': 'ipmask', 'subnet': '192.168.1.0/24', 'comment': 'Internal LAN'},
            {'name': 'dmz_subnet', 'type': 'ipmask', 'subnet': '10.0.1.0/24', 'comment': 'DMZ network'},
            {'name': 'web_server', 'type': 'ipmask', 'subnet': '10.0.1.100/32', 'comment': 'Web server'},
            {'name': 'mail_server', 'type': 'ipmask', 'subnet': '10.0.1.200/32', 'comment': 'Mail server'},
            {'name': 'remote_office', 'type': 'ipmask', 'subnet': '172.16.0.0/16', 'comment': 'Remote office network'},
            {'name': 'dynamic_range', 'type': 'iprange', 'start-ip': '192.168.100.1', 'end-ip': '192.168.100.100'},
            {'name': 'google_dns', 'type': 'fqdn', 'fqdn': 'dns.google.com', 'comment': 'Google DNS'},
        ]
        
        # Service objects
        services = [
            {'name': 'Custom_HTTP_8080', 'category': 'Web Access', 'protocol': 'TCP', 'tcp-portrange': '8080'},
            {'name': 'Custom_App_9000', 'category': 'General', 'protocol': 'TCP', 'tcp-portrange': '9000-9010'},
            {'name': 'SNMP_Custom', 'category': 'Network Services', 'protocol': 'UDP', 'udp-portrange': '161'},
            {'name': 'Database_Services', 'category': 'Database', 'protocol': 'TCP', 'tcp-portrange': '3306,5432,1433'},
        ]
        
        # Address groups
        address_groups = [
            {'name': 'Internal_Networks', 'member': [{'name': 'internal_subnet'}, {'name': 'dmz_subnet'}]},
            {'name': 'Servers', 'member': [{'name': 'web_server'}, {'name': 'mail_server'}]},
            {'name': 'Remote_Sites', 'member': [{'name': 'remote_office'}]},
        ]
        
        # Service groups
        service_groups = [
            {'name': 'Web_Services', 'member': [{'name': 'HTTP'}, {'name': 'HTTPS'}, {'name': 'Custom_HTTP_8080'}]},
            {'name': 'Database_Access', 'member': [{'name': 'Database_Services'}]},
        ]
        
        # Map to endpoints
        for addr in addresses:
            objects_data.append({'endpoint': '/cmdb/firewall/address', 'data': addr, 'category': 'firewall_objects'})
            
        for svc in services:
            objects_data.append({'endpoint': '/cmdb/firewall/service/custom', 'data': svc, 'category': 'firewall_objects'})
            
        for grp in address_groups:
            objects_data.append({'endpoint': '/cmdb/firewall/addrgrp', 'data': grp, 'category': 'firewall_objects'})
            
        for grp in service_groups:
            objects_data.append({'endpoint': '/cmdb/firewall/service/group', 'data': grp, 'category': 'firewall_objects'})
        
        return objects_data
    
    def generate_routing_data(self) -> List[Dict[str, Any]]:
        """Generate routing configuration data"""
        routing_data = []
        
        # Static routes
        static_routes = [
            {'seq-num': 1, 'dst': '0.0.0.0/0', 'gateway': '192.168.1.1', 'device': 'port1', 'distance': 10},
            {'seq-num': 2, 'dst': '10.0.0.0/8', 'gateway': '192.168.1.254', 'device': 'port2', 'distance': 20},
            {'seq-num': 3, 'dst': '172.16.0.0/12', 'gateway': '10.0.1.1', 'device': 'tunnel1', 'distance': 1},
            {'seq-num': 4, 'dst': '8.8.8.8/32', 'gateway': '192.168.1.1', 'device': 'port1', 'distance': 5},
        ]
        
        # Policy routes
        policy_routes = [
            {'seq-num': 1, 'input-device': 'port2', 'src': '192.168.2.0/24', 'dst': '0.0.0.0/0', 'gateway': '10.0.1.1'},
            {'seq-num': 2, 'input-device': 'port3', 'protocol': 6, 'start-port': 80, 'end-port': 80, 'gateway': '10.0.2.1'},
        ]
        
        # BGP configuration
        bgp_configs = [
            {'as': 65001, 'router-id': '10.0.0.1', 'neighbor': [{'ip': '10.0.1.2', 'remote-as': 65002}]},
            {'as': 65001, 'network': [{'prefix': '192.168.1.0', 'netmask': '255.255.255.0'}]},
        ]
        
        # Map to endpoints
        for route in static_routes:
            routing_data.append({'endpoint': '/cmdb/router/static', 'data': route, 'category': 'routing'})
            
        for route in policy_routes:
            routing_data.append({'endpoint': '/cmdb/router/policy', 'data': route, 'category': 'routing'})
            
        for bgp in bgp_configs:
            routing_data.append({'endpoint': '/cmdb/router/bgp', 'data': bgp, 'category': 'routing'})
        
        return routing_data
    
    def generate_system_data(self) -> List[Dict[str, Any]]:
        """Generate system configuration data"""
        system_data = []
        
        # Interfaces
        interfaces = [
            {'name': 'port1', 'ip': '192.168.1.1/24', 'allowaccess': ['ping', 'https', 'ssh'], 'type': 'physical', 'status': 'up'},
            {'name': 'port2', 'ip': '10.0.1.1/24', 'allowaccess': ['ping'], 'type': 'physical', 'status': 'up'},
            {'name': 'port3', 'mode': 'switch', 'type': 'physical', 'status': 'up'},
            {'name': 'tunnel1', 'ip': '169.254.1.1/30', 'type': 'tunnel', 'interface': 'port1', 'status': 'up'},
            {'name': 'ssl.root', 'ip': '10.212.134.1/24', 'type': 'tunnel', 'status': 'up'},
        ]
        
        # Global settings
        global_settings = [
            {'hostname': 'FortiGate-Branch-01', 'timezone': '04'},
            {'admin-sport': 8443, 'admin-ssh-port': 2222},
            {'gui-theme': 'blue', 'gui-date-format': 'yyyy/mm/dd'},
        ]
        
        # Admin users
        admin_users = [
            {'name': 'admin', 'trusthost1': '192.168.1.0/24', 'accprofile': 'super_admin'},
            {'name': 'operator', 'trusthost1': '192.168.1.0/24', 'accprofile': 'prof_admin'},
            {'name': 'readonly', 'trusthost1': '0.0.0.0/0', 'accprofile': 'readonly'},
        ]
        
        # System status (monitoring)
        status_data = [
            {'hostname': 'FortiGate-100D', 'model': 'FortiGate-100D', 'serial': 'FGT60E1234567890', 
             'version': 'v7.0.0', 'build': '0366', 'uptime': 1234567, 'cpu': 15, 'memory': 35},
            {'interface-stats': [
                {'name': 'port1', 'rx_bytes': 123456789, 'tx_bytes': 987654321, 'rx_packets': 45678, 'tx_packets': 56789}
            ]},
        ]
        
        # Map to endpoints
        for intf in interfaces:
            system_data.append({'endpoint': '/cmdb/system/interface', 'data': intf, 'category': 'system'})
            
        for setting in global_settings:
            system_data.append({'endpoint': '/cmdb/system/global', 'data': setting, 'category': 'system'})
            
        for admin in admin_users:
            system_data.append({'endpoint': '/cmdb/system/admin', 'data': admin, 'category': 'system'})
            
        for status in status_data:
            system_data.append({'endpoint': '/monitor/system/status', 'data': status, 'category': 'monitor'})
        
        return system_data
    
    def generate_vpn_data(self) -> List[Dict[str, Any]]:
        """Generate VPN configuration data"""
        vpn_data = []
        
        # IPSec Phase 1
        phase1_configs = [
            {
                'name': 'VPN_HQ', 'interface': 'port1', 'ike-version': 2, 'type': 'static',
                'remote-gw': '203.0.113.10', 'proposal': 'aes256-sha256', 'dhgrp': '14',
                'keylife': 28800, 'local-gw': '0.0.0.0', 'psksecret': 'encrypted'
            },
            {
                'name': 'VPN_Branch_02', 'interface': 'port1', 'ike-version': 1, 'type': 'static',
                'remote-gw': '198.51.100.20', 'proposal': 'aes128-sha1', 'dhgrp': '2',
                'keylife': 86400, 'nattraversal': 'enable'
            },
        ]
        
        # IPSec Phase 2
        phase2_configs = [
            {
                'name': 'VPN_HQ_P2', 'phase1name': 'VPN_HQ', 'proposal': 'aes256-sha256',
                'dhgrp': '14', 'keylifeseconds': 3600, 'src-subnet': '192.168.1.0/24',
                'dst-subnet': '10.0.0.0/8'
            },
        ]
        
        # SSL VPN settings
        sslvpn_configs = [
            {
                'status': 'enable', 'port': 443, 'source-interface': ['port1'],
                'source-address': ['all'], 'tunnel-ip-pools': ['SSLVPN_TUNNEL_ADDR1'],
                'tunnel-ipv6-pools': [], 'dns-server1': '8.8.8.8', 'dns-server2': '8.8.4.4'
            },
        ]
        
        # VPN monitoring data
        vpn_monitor = [
            {
                'name': 'VPN_HQ', 'status': 'up', 'rgwy': '203.0.113.10',
                'incoming_bytes': 10485760, 'outgoing_bytes': 20971520, 'uptime': 86400
            },
        ]
        
        # Map to endpoints
        for p1 in phase1_configs:
            vpn_data.append({'endpoint': '/cmdb/vpn/ipsec/phase1-interface', 'data': p1, 'category': 'vpn'})
            
        for p2 in phase2_configs:
            vpn_data.append({'endpoint': '/cmdb/vpn/ipsec/phase2-interface', 'data': p2, 'category': 'vpn'})
            
        for ssl in sslvpn_configs:
            vpn_data.append({'endpoint': '/cmdb/vpn/ssl/settings', 'data': ssl, 'category': 'vpn'})
            
        for monitor in vpn_monitor:
            vpn_data.append({'endpoint': '/monitor/vpn/ipsec', 'data': monitor, 'category': 'monitor'})
        
        return vpn_data
    
    def generate_user_auth_data(self) -> List[Dict[str, Any]]:
        """Generate user authentication data"""
        user_data = []
        
        # Local users
        local_users = [
            {'name': 'john.doe', 'status': 'enable', 'type': 'password', 'email-to': 'john.doe@company.com'},
            {'name': 'jane.smith', 'status': 'enable', 'type': 'password', 'two-factor': 'fortitoken'},
            {'name': 'guest_user', 'status': 'enable', 'type': 'password', 'workstation': '192.168.1.100'},
        ]
        
        # User groups
        user_groups = [
            {'name': 'VPN_Users', 'member': [{'name': 'john.doe'}, {'name': 'jane.smith'}]},
            {'name': 'Guest_Users', 'member': [{'name': 'guest_user'}]},
        ]
        
        # LDAP servers
        ldap_servers = [
            {
                'name': 'Company_AD', 'server': '192.168.1.10', 'cnid': 'cn',
                'dn': 'dc=company,dc=com', 'type': 'simple', 'port': 389
            },
        ]
        
        # RADIUS servers
        radius_servers = [
            {
                'name': 'NPS_Server', 'server': '192.168.1.20', 'secret': 'encrypted',
                'auth-type': 'auto', 'nas-ip': '192.168.1.1'
            },
        ]
        
        # Map to endpoints
        for user in local_users:
            user_data.append({'endpoint': '/cmdb/user/local', 'data': user, 'category': 'user_auth'})
            
        for group in user_groups:
            user_data.append({'endpoint': '/cmdb/user/group', 'data': group, 'category': 'user_auth'})
            
        for ldap in ldap_servers:
            user_data.append({'endpoint': '/cmdb/user/ldap', 'data': ldap, 'category': 'user_auth'})
            
        for radius in radius_servers:
            user_data.append({'endpoint': '/cmdb/user/radius', 'data': radius, 'category': 'user_auth'})
        
        return user_data
    
    def generate_security_profiles_data(self) -> List[Dict[str, Any]]:
        """Generate security profiles data"""
        security_data = []
        
        # Antivirus profiles
        av_profiles = [
            {
                'name': 'strict_av', 'scan-mode': 'full', 'outbreak-prevention': 'enable',
                'http': {'options': 'scan'}, 'ftp': {'options': 'scan'}, 'smtp': {'options': 'scan'}
            },
            {'name': 'basic_av', 'scan-mode': 'quick', 'http': {'options': 'scan'}},
        ]
        
        # IPS sensors
        ips_sensors = [
            {
                'name': 'high_security', 'block-malicious-url': 'enable',
                'entries': [
                    {'id': 1, 'rule': [{'id': 15227}], 'action': 'block', 'severity': 'high'},
                    {'id': 2, 'rule': [{'id': 32315}], 'action': 'block', 'severity': 'critical'}
                ]
            },
        ]
        
        # Application control lists
        app_lists = [
            {
                'name': 'block_high_risk', 'default-network-services': 'enable',
                'entries': [
                    {'id': 1, 'category': [{'id': 2}], 'action': 'block'},  # P2P
                    {'id': 2, 'category': [{'id': 6}], 'action': 'block'},  # Proxy
                ]
            },
        ]
        
        # Web filter profiles
        webfilter_profiles = [
            {
                'name': 'strict', 'https-replacemsg': 'enable', 'ovrd': 'allow',
                'filters': [
                    {'id': 1, 'category': 26, 'action': 'block'},  # Adult/Mature Content
                    {'id': 2, 'category': 61, 'action': 'warning'},  # Social Media
                ]
            },
        ]
        
        # Map to endpoints
        for av in av_profiles:
            security_data.append({'endpoint': '/cmdb/antivirus/profile', 'data': av, 'category': 'security_profiles'})
            
        for ips in ips_sensors:
            security_data.append({'endpoint': '/cmdb/ips/sensor', 'data': ips, 'category': 'security_profiles'})
            
        for app in app_lists:
            security_data.append({'endpoint': '/cmdb/application/list', 'data': app, 'category': 'security_profiles'})
            
        for web in webfilter_profiles:
            security_data.append({'endpoint': '/cmdb/webfilter/profile', 'data': web, 'category': 'security_profiles'})
        
        return security_data
    
    def generate_monitoring_data(self) -> List[Dict[str, Any]]:
        """Generate monitoring and log data"""
        monitor_data = []
        
        # System performance
        performance_data = [
            {
                'cpu': random.randint(10, 80), 'memory': random.randint(20, 70),
                'disk': random.randint(5, 50), 'sessions': random.randint(100, 5000),
                'timestamp': datetime.now().isoformat()
            }
            for _ in range(5)
        ]
        
        # Firewall sessions
        session_data = [
            {
                'sessions': [
                    {
                        'sessionid': i, 'src': f'192.168.1.{random.randint(10, 250)}',
                        'dst': f'8.8.{random.randint(1, 8)}.{random.randint(1, 8)}',
                        'proto': 6, 'sport': random.randint(1024, 65535), 'dport': random.choice([80, 443, 53]),
                        'duration': random.randint(1, 3600), 'bytes': random.randint(1024, 1048576)
                    }
                    for i in range(10)
                ]
            }
        ]
        
        # Interface statistics
        interface_stats = [
            {
                'name': 'port1', 'rx_bytes': random.randint(1000000, 100000000),
                'tx_bytes': random.randint(1000000, 100000000),
                'rx_packets': random.randint(1000, 100000), 'tx_packets': random.randint(1000, 100000),
                'rx_errors': random.randint(0, 100), 'tx_errors': random.randint(0, 100)
            }
            for port in ['port1', 'port2', 'port3']
        ]
        
        # Map to endpoints
        for perf in performance_data:
            monitor_data.append({'endpoint': '/monitor/system/performance', 'data': perf, 'category': 'monitor'})
            
        for session in session_data:
            monitor_data.append({'endpoint': '/monitor/firewall/session', 'data': session, 'category': 'monitor'})
            
        for stat in interface_stats:
            monitor_data.append({'endpoint': '/monitor/system/interface', 'data': stat, 'category': 'monitor'})
        
        return monitor_data
    
    def generate_all_training_data(self) -> Dict[str, Any]:
        """Generate comprehensive training data for all categories"""
        all_examples = []
        
        # Generate data for each category
        generators = [
            self.generate_firewall_policy_data,
            self.generate_firewall_objects_data,
            self.generate_routing_data,
            self.generate_system_data,
            self.generate_vpn_data,
            self.generate_user_auth_data,
            self.generate_security_profiles_data,
            self.generate_monitoring_data,
        ]
        
        for generator in generators:
            examples = generator()
            for example in examples:
                # Add timestamp and features
                example['timestamp'] = datetime.now().isoformat()
                example['features'] = self._extract_features(example['endpoint'], example['data'])
                example['synthetic'] = True
                example['enhanced'] = True
            all_examples.extend(examples)
        
        # Add some variability with timestamps
        base_time = datetime.now() - timedelta(days=30)
        for i, example in enumerate(all_examples):
            example['timestamp'] = (base_time + timedelta(hours=i)).isoformat()
        
        training_data = {
            'examples': all_examples,
            'categories': list(self.categories.keys()),
            'category_descriptions': self.categories,
            'total_examples': len(all_examples),
            'enhanced_dataset': True,
            'generation_date': datetime.now().isoformat(),
            'generator_version': '2.0'
        }
        
        return training_data
    
    def _extract_features(self, endpoint: str, data: Any) -> str:
        """Extract features from endpoint and data for training"""
        features = []
        
        # Endpoint features
        endpoint_parts = endpoint.lower().replace('/cmdb', '').replace('/monitor', '').replace('/api/v2', '').split('/')
        features.extend([part for part in endpoint_parts if part])
        
        # Data features
        if isinstance(data, dict):
            features.extend(data.keys())
            # Add some value-based features for better classification
            for key, value in data.items():
                if isinstance(value, str):
                    if any(term in value.lower() for term in ['enable', 'disable']):
                        features.append(f'{key}_status')
                    elif any(term in value.lower() for term in ['accept', 'deny', 'block']):
                        features.append(f'{key}_action')
                elif isinstance(value, list) and value:
                    features.append(f'{key}_list')
        
        return ' '.join(features)


def main():
    """Generate enhanced training data and save to file"""
    print("🚀 Generating Enhanced Training Data for FortiGate API ML/AI Components")
    print("=" * 70)
    
    generator = EnhancedTrainingDataGenerator()
    
    # Generate comprehensive training data
    print("📊 Generating training data for all categories...")
    training_data = generator.generate_all_training_data()
    
    print(f"✅ Generated {training_data['total_examples']} training examples")
    print(f"📚 Categories included: {len(training_data['categories'])}")
    
    # Category breakdown
    category_counts = {}
    for example in training_data['examples']:
        cat = example['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\n📈 Category Distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category:20} : {count:3d} examples")
    
    # Save to file
    ml_components_dir = os.path.join(os.path.dirname(__file__), 'ml_components')
    training_data_dir = os.path.join(ml_components_dir, 'training_data')
    os.makedirs(training_data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"enhanced_training_data_{timestamp}.json"
    filepath = os.path.join(training_data_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"\n💾 Enhanced training data saved to: {filename}")
    print(f"📁 Full path: {filepath}")
    print("\n🎯 This dataset can now be used to train more accurate ML models!")
    
    return filepath


if __name__ == "__main__":
    main()
