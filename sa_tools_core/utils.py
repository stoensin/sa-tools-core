# coding: utf-8

from __future__ import print_function

import os
import sys
import pwd
import socket
from functools import wraps

from sa_tools_core.consts import CONFIG_DIR

HOSTS_FILE = '/etc/hosts'
HOSTS_WAN_FILE = '/etc/hosts.wan'

ip_hostname_cache = {}


def get_os_username():
    return pwd.getpwuid(os.getuid()).pw_name


def get_config(config_name):
    try:
        with open(os.path.join(CONFIG_DIR, config_name)) as f:
            config = f.read()
    except IOError as e:
        if e.errno == 2:
            print('Error: get config failed, you shall not execute this program on this machine!',
                  file=sys.stderr)
            sys.exit(1)
        raise
    return config.strip()


def resolve_hostname(hostname):
    return socket.gethostbyname(hostname)


def resolve_ip(ip):
    from sh import grep

    if ip_hostname_cache.get(ip):
        return ip_hostname_cache[ip]
    hostname = ip
    # tricky
    if ip.startswith('192.') or ip.startswith('10.'):
        hosts_files = (HOSTS_FILE,)
    else:
        hosts_files = (HOSTS_WAN_FILE,)
    for hosts_file in hosts_files:
        try:
            out = grep('^[^#]*%s[^0-9]' % ip, hosts_file, E=True)
            if out:
                hostname = out.split()[-1]
                break
        except Exception:
            pass
    ip_hostname_cache[ip] = hostname
    return hostname


def reverse_func(f):
    """ reverse function Boolean result """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return not f(*args, **kwargs)
    return wrapper
