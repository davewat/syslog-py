# Copyright (c) 2016, Alexander Böhm - pysyslogclient
# Copyright (c) 2020, Maciej Budzyński - syslog-py
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

version = "0.2.5"

import socket
from datetime import datetime


def datetime2rfc3339(dt, is_utc=False):
    if is_utc is False:
        # calculating timezone
        d1 = datetime.now()
        d2 = datetime.utcnow()
        diff_hr = (d1 - d2).seconds / 60 / 60
        tz = ""

        if diff_hr == 0:
            tz = "Z"
        else:
            if diff_hr > 0:
                tz = "+%s" % (tz)

            tz = "%s%.2d%.2d" % (tz, diff_hr, 0)

        return "%s%s" % (dt.strftime("%Y-%m-%dT%H:%M:%S.%f"), tz)

    else:
        return dt.isoformat() + 'Z'


FAC_KERNEL = 0
FAC_USER = 1
FAC_MAIL = 2
FAC_SYSTEM = 3
FAC_SECURITY = 4
FAC_SYSLOG = 5
FAC_PRINTER = 6
FAC_NETWORK = 7
FAC_UUCP = 8
FAC_CLOCK = 9
FAC_AUTH = 10
FAC_FTP = 11
FAC_NTP = 12
FAC_LOG_AUDIT = 13
FAC_LOG_ALERT = 14
FAC_CLOCK2 = 15
FAC_LOCAL0 = 16
FAC_LOCAL1 = 17
FAC_LOCAL2 = 18
FAC_LOCAL3 = 19
FAC_LOCAL4 = 20
FAC_LOCAL5 = 21
FAC_LOCAL6 = 22
FAC_LOCAL7 = 23

SEV_EMERGENCY = 0
SEV_ALERT = 1
SEV_CRITICAL = 2
SEV_ERROR = 3
SEV_WARNING = 4
SEV_NOTICE = 5
SEV_INFO = 6
SEV_DEBUG = 7

OCTET_COUNTING = 0
OCTET_STUFFING = 1

TRAILER_LF = 0
TRAILER_CRLF = 1
TRAILER_NULL = 2


class SyslogClient(object):
    """
    >>> client = SyslogClient("localhost", 10514)
    >>> client.log("test")
    """

    def __init__(self,
                 server: str,
                 port: int,
                 proto: str = 'tcp',
                 force_ipv4: bool = False,
                 client_name: str = None,
                 rfc: str = None,
                 max_message_length: int = 1024,
                 octet: int = OCTET_COUNTING,
                 trailer: int = TRAILER_LF) -> None:
        self.socket = None
        self.server = server
        self.port = port
        self.proto = socket.SOCK_DGRAM
        self.rfc = rfc
        self.max_message_length = max_message_length
        self.force_ipv4 = force_ipv4
        self.octet = octet
        self.trailer = trailer

        if proto is not None:
            if proto.upper() == 'UDP':
                self.proto = socket.SOCK_DGRAM
            elif proto.upper() == 'TCP':
                self.proto = socket.SOCK_STREAM

        if client_name is None:
            self.client_name = socket.getfqdn()
            if self.client_name is None:
                self.client_name = socket.gethostname()

    def connect(self) -> bool:
        if self.socket is None:
            r = socket.getaddrinfo(self.server, self.port, socket.AF_UNSPEC, self.proto)
            if r is None:
                return False

            for (addr_fam, sock_kind, proto, ca_name, sock_addr) in r:
                self.socket = socket.socket(addr_fam, self.proto)
                if self.socket is None:
                    return False

                try:
                    self.socket.connect(sock_addr)
                    return True

                except socket.timeout as e:
                    if self.socket is not None:
                        self.socket.close()
                        self.socket = None
                    continue

                # ensure python 2.x compatibility
                except socket.error as e:
                    if self.socket is not None:
                        self.socket.close()
                        self.socket = None
                    continue

            return False

        else:
            return True

    def close(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def log(self, message: str, timestamp: datetime = None, is_utc: bool = None, hostname: str = None,
            facility: int = None, severity: int = None, octet: int = None) -> None:
        pass

    def send(self, message_data: str) -> None:
        if self.socket is not None or self.connect():
            try:
                if self.max_message_length is not None:
                    self.socket.sendall(message_data[:self.max_message_length])
                else:
                    self.socket.sendall(message_data)
            except IOError as e:
                self.close()

    def _get_trailer(self):
        if self.trailer is TRAILER_LF:
            return "\n"
        elif self.trailer is TRAILER_CRLF:
            return "\r\n"
        else:
            return "\0"

    def _build_octet_message(self, octet, d):
        if OCTET_COUNTING is self._get_octet(octet):
            return str(len(d)) + " " + d
        else:
            return d + self._get_trailer()

    def _get_octet(self, octet):
        if self.proto is socket.SOCK_STREAM:
            return octet if octet is not None else self.octet
        else:
            return OCTET_STUFFING


class SyslogClientRFC5424(SyslogClient):
    """
    >>> client = SyslogClientRFC5424("localhost", 10514, proto='udp')
    >>> client.log("test")
    >>> client = SyslogClientRFC5424("localhost", 10514, proto='tcp')
    >>> client.log("test")
    """

    def __init__(self,
                 server: str,
                 port: int,
                 proto: str = 'tcp',
                 force_ipv4: bool = False,
                 client_name: str = None,
                 octet: int = OCTET_COUNTING,
                 trailer: int = TRAILER_LF) -> None:
        SyslogClient.__init__(self,
                              server=server,
                              port=port,
                              proto=proto,
                              force_ipv4=force_ipv4,
                              client_name=client_name,
                              rfc='5424',
                              max_message_length=1024 * 8,
                              octet=octet,
                              trailer=trailer
                              )

    def log(self, message: str, facility: int = None, severity: int = None, timestamp: datetime = None,
            is_utc: bool = None, hostname: str = None, version: int = 1, program: str = None, pid: int = None,
            msg_id: int = None, octet: int = None):
        if facility is None:
            facility = FAC_USER

        if severity is None:
            severity = SEV_INFO

        pri = facility * 8 + severity

        if timestamp is None:
            timestamp_s = datetime2rfc3339(datetime.utcnow(), is_utc=True)
        else:
            if is_utc is None:
                timestamp_s = datetime2rfc3339(timestamp, is_utc=False)
            else:
                timestamp_s = datetime2rfc3339(timestamp, is_utc=is_utc)

        if hostname is None:
            hostname_s = self.client_name
        else:
            hostname_s = hostname

        if program is None:
            appname_s = "-"
        else:
            appname_s = program

        if pid is None:
            procid_s = "-"
        else:
            procid_s = pid

        if msg_id is None:
            msgid_s = "-"
        else:
            msgid_s = msg_id

        d = "<%i>%i %s %s %s %s %s %s" % (
            pri,
            version,
            timestamp_s,
            hostname_s,
            appname_s,
            procid_s,
            msgid_s,
            message
        )

        d = self._build_octet_message(octet, d)

        self.send(d.encode('utf-8'))


class SyslogClientRFC3164(SyslogClient):
    """
    >>> client = SyslogClientRFC3164("localhost", 10514, proto='udp')
    >>> client.log("test")
    >>> client = SyslogClientRFC3164("localhost", 10514, proto='tcp')
    >>> client.log("test")
    """

    def __init__(self,
                 server: str,
                 port: int,
                 proto: str = 'tcp',
                 force_ipv4: bool = False,
                 client_name: str = None,
                 octet: int = OCTET_COUNTING,
                 trailer: int = TRAILER_LF) -> None:
        SyslogClient.__init__(self,
                              server=server,
                              port=port,
                              proto=proto,
                              force_ipv4=force_ipv4,
                              client_name=client_name,
                              rfc='3164',
                              max_message_length=1024,
                              octet=octet,
                              trailer=trailer
                              )

    def log(self, message: str, facility: int = None, severity: int = None,
            timestamp: datetime = None, is_utc: bool = None, hostname: str = None, program: str = "SyslogClient",
            pid: int = None, octet: int = None) -> None:
        if facility is None:
            facility = FAC_USER

        if severity is None:
            severity = SEV_INFO

        pri = facility * 8 + severity

        if timestamp is None:
            t = datetime.now()
        else:
            t = timestamp

        timestamp_s = t.strftime("%b %d %H:%M:%S")

        if hostname is None:
            hostname_s = self.client_name
        else:
            hostname_s = hostname

        tag_s = ""
        if program is None:
            tag_s += "SyslogClient"
        else:
            tag_s += program

        if pid is not None:
            tag_s += "[%i]" % pid

        d = "<%i>%s %s %s: %s" % (
            pri,
            timestamp_s,
            hostname_s,
            tag_s,
            message
        )

        d = self._build_octet_message(octet, d)

        self.send(d.encode('ASCII', 'ignore'))


if __name__ == '__main__':
    import doctest

    doctest.testmod()
