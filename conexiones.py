import pwd
import os
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import glob

PROC_TCP = "/proc/net/tcp"
STATE = {
        '01': 'ESTABLECIDA',
        '02': 'SYN_SENT',
        '03': 'SYN_RECV',
        '04': 'FIN_WAIT1',
        '05': 'FIN_WAIT2',
        '06': 'TIME_WAIT',
        '07': 'CERRADA',
        '08': 'CLOSE_WAIT',
        '09': 'LAST_ACK',
        '0A': 'ESCUCHANDO',
        '0B': 'CERRANDO'
        }


def _hex2dec(s):
    return str(int(s, 16))


def _ip(s):
    ip = [(_hex2dec(s[6:8])), (_hex2dec(s[4:6])), (_hex2dec(s[2:4])), (_hex2dec(s[0:2]))]
    return '.'.join(ip)


def _remove_empty(array):
    return [x for x in array if x != '']


def _convert_ip_port(array):
    host, port = array.split(':')
    return _ip(host), _hex2dec(port)


def netstat(content):
    '''
    Esta funcion devuelve una lista de conexiones tcp de equipos linux
    '''

    result = []
    for line in content:
        line_array = _remove_empty(line.split(' '))     # Quita espacio vacios y crea lista.
        l_host, l_port = _convert_ip_port(line_array[1]) # Convierte direcciones ip y puertos de hexadecimal a decimal.
        r_host, r_port = _convert_ip_port(line_array[2])
        tcp_id = line_array[0]
        state = STATE[line_array[3]]
        uid = pwd.getpwuid(int(line_array[7]))[0]       # Captura el usuario por UID.
        inode = line_array[9]
        pid = _get_pid_of_inode(inode)
        try:
            exe = os.readlink('/proc/' + pid + '/exe')
        except:
            exe = None

        nline = [tcp_id, uid, l_host + ':' + l_port, r_host + ':' + r_port, state, pid, exe]
        result.append(nline)
    return result


def _get_pid_of_inode(inode):

    for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode, os.readlink(item)):
                return item.split('/')[2]
        except:
            pass
    return None

