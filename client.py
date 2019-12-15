#!/usr/bin/env python
# :author: Fabio "BlackLight" Manganiello <info@fabiomanganiello.com>
#
# Requirements:
#     - `requests` package (`pip install requests`)
#     - [Advised] static IP allocation for your WeMo devices

import argparse
import enum
import ipaddress
import json
import re
import requests
import socket
import sys
import textwrap

from xml.dom.minidom import parseString


default_port = 49153


class SwitchAction(enum.Enum):
    GET_STATE = 'GetBinaryState'
    SET_STATE = 'SetBinaryState'
    GET_NAME = 'GetFriendlyName'


def _exec(device: str, action: SwitchAction, value=None, port: int = default_port, timeout: float = None):
    state_name = action.value[3:]

    response = requests.post(
        'http://{}:{}/upnp/control/basicevent1'.format(device, port),
        headers={
            'User-Agent': '',
            'Accept': '',
            'Content-Type': 'text/xml; charset="utf-8"',
            'SOAPACTION': '\"urn:Belkin:service:basicevent:1#{}\"'.format(action.value),
        },
        data=re.sub('\s+', ' ', textwrap.dedent(
            '''
            <?xml version="1.0" encoding="utf-8"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <s:Body>
                    <u:{action} xmlns:u="urn:Belkin:service:basicevent:1">
                        <{state}>{value}</{state}>
                    </u:{action}
                ></s:Body>
            </s:Envelope>
            '''.format(action=action.value, state=state_name,
                       value=value if value is not None else ''))))

    dom = parseString(response.text)
    return dom.getElementsByTagName(state_name).item(0).firstChild.data


def on(device: str, *args, **kwargs):
    return _exec(device, SwitchAction.SET_STATE, 1)


def off(device: str, *args, **kwargs):
    return _exec(device, SwitchAction.SET_STATE, 0, *args, **kwargs)


def get_state(device: str, *args, **kwargs):
    return bool(int(_exec(device, SwitchAction.GET_STATE, *args, **kwargs)))


def get_name(device: str, *args, **kwargs):
    return _exec(device, SwitchAction.GET_NAME, *args, **kwargs)


def get_device(device: str, *args, **kwargs):
    return {
        'device': device,
        'name': get_name(device, *args, **kwargs),
        'state': get_state(device, *args, **kwargs),
    }


def main():
    global default_port

    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', '-s', dest='scan', required=False, default=False, action='store_true',
                        help="Run Switchbot in scan mode - scan devices to control")

    parser.add_argument('--subnet', '-n', dest='subnet', required=False, default=None,
                        help="Set the network subnet for --scan mode (e.g. 192.168.1.0/24)")

    parser.add_argument('--port', '-p', dest='port', required=False, type=int, default=default_port,
                        help="TCP port used by the WeMo device(s)")

    parser.add_argument('--scan-timeout', dest='scan_timeout', type=float, required=False, default=2.0,
                        help="Device scan timeout (default: 2 seconds)")

    parser.add_argument('--connect-timeout', dest='connect_timeout', type=float, required=False, default=30.0,
                        help="Device connection timeout (default: 30 seconds)")

    # parser.add_argument('--connect-timeout', dest='connect_timeout', required=False, default=None,
    #                     help="Device connection timeout (default: 5 seconds)")

    parser.add_argument('--device', '-d', dest='device', required=False, default=None,
                        help="IP address of a device to control")

    parser.add_argument('--on', dest='on', required=False, default=False, action='store_true',
                        help="Turn the device on")

    parser.add_argument('--off', dest='off', required=False, default=False, action='store_true',
                        help="Turn the device off")

    parser.add_argument('--toggle', dest='toggle', required=False, default=False, action='store_true',
                        help="Toggle the device")

    opts, args = parser.parse_known_args(sys.argv[1:])

    if (opts.scan and opts.device) or not (opts.scan or opts.device):
        raise AttributeError('Please specify either --scan or --device')

    if opts.scan:
        if not opts.subnet:
            raise AttributeError('No --subnet specified for --scan mode')

        devices = []

        for addr in ipaddress.IPv4Network(opts.subnet):
            try:
                print('Scanning device {}'.format(addr.exploded))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(opts.scan_timeout)
                sock.connect((addr.exploded, opts.port))
                sock.close()
                dev = get_device(addr.exploded, timeout=opts.connect_timeout)
                devices.append(dev)
                print(dev)
            except OSError as e:
                pass

        print('Found {} WeMo devices'.format(len(devices)))
        print(json.dumps(devices, indent=2))
        return

    _on = opts.on
    _off = opts.off

    if opts.toggle:
        if get_state(opts.device):
            _off = True
        else:
            _on = True

    if _on:
        on(opts.device, timeout=opts.connect_timeout)
    elif _off:
        off(opts.device, timeout=opts.connect_timeout)
    else:
        print(json.dumps(
            get_device(opts.device, timeout=opts.connect_timeout),
            indent=2))


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:
