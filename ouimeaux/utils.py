import time
import socket
import struct
import re


def tz_hours():
    delta = time.localtime().tm_hour - time.gmtime().tm_hour
    sign = '-' if delta < 0 else ''
    return "%s%02d.00" % (sign, abs(delta))


def is_dst():
    return 1 if time.localtime().tm_isdst else 0


def get_timesync():
    timesync = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>
  <u:TimeSync xmlns:u="urn:Belkin:service:timesync:1">
   <UTC>{utc}</UTC>
   <TimeZone>{tz}</TimeZone>
   <dst>{dst}</dst>
   <DstSupported>{dstsupported}</DstSupported>
  </u:TimeSync>
 </s:Body>
</s:Envelope>""".format(
        utc=int(time.time()),
        tz=tz_hours(),
        dst=is_dst(),
        dstsupported=is_dst()).strip()
    return timesync


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('1.2.3.4', 9))
        return s.getsockname()[0]
    except socket.error:
        return None
    finally:
        del s


def matcher(match_string):
    pattern = re.compile('.*?'.join(re.escape(c) for c in match_string.lower()))
    def matches(s):
        return pattern.search(s.lower()) is not None
    return matches

