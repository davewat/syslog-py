# pysyslogclient

Syslog client for Python 3 (RFC 3164/5424) for UNIX and Windows

## Description

Syslog client following

* RFC3164 (https://www.ietf.org/rfc/rfc3164.txt)
* RFC5424 (https://www.ietf.org/rfc/rfc5424.txt)
* RFC6587 (https://www.ietf.org/rfc/rfc6587.txt) - for syslog over TCP

with UNIX and Windows support. TCP and UDP transport is possible.

If TCP is used, on every log message, that is send to the specified server,
and a connection error occured, the message will be dismissed and
a reconnect will be tried for the next message.

## Usage

A small CLI client is implemented in *client.py*. To call it, run

```
python -m pysyslogclient.cli
```

### Startup client 

To setup the client for RFC 5424 over TCP to send to SERVER:PORT:

```
import pysyslogclient
client = pysyslogclient.SyslogClientRFC5424(SERVER, PORT, proto="TCP")
```

or for RFC3164:

```
import SyslogClient
client = pysyslogclient.SyslogClientRFC3164(SERVER, PORT, proto="TCP")
```

### Log a messsage

Log the message "Hello syslog server" with standard severity *INFO* as facility
*USER*. As program name *SyslogClient* the PID of the called python interpreter
is used.

```
client.log("Hello syslog server")

```

To specify more options, call log with more arguments. For example to log
the message as program *Logger* with PID *1* as facility *SYSTEM* with severity
*EMERGENCY*, call log the following way:

```
client.log("Hello syslog server",
	facility=pysyslogclient.FAC_SYSTEM,
	severity=pysyslogclient.SEV_EMERGENCY,
	program="Logger",
	pid=1)
```

For TCP protocol, the octet parameter is available in client constructor and in log method.
The parameter in log method has precedence over constructor parameter.
In case of UDP protocol, octet parameter is ignored.

Below in the first message, octet stuffing is in use, in second octet counting (forced by octet parameter in log method).
```
import pysyslogclient
client = pysyslogclient.SyslogClientRFC5424(SERVER, PORT, proto="TCP", octet="OCTET_STUFFING")

client.log("Hello syslog server",
	facility=pysyslogclient.FAC_SYSTEM,
	severity=pysyslogclient.SEV_EMERGENCY,
	program="Logger",
	pid=1)

client.log("Hello syslog server",
	facility=pysyslogclient.FAC_SYSTEM,
	severity=pysyslogclient.SEV_EMERGENCY,
	program="Logger",
	pid=1,
	octet=OCTET_COUNGING)
```

### Shutdown

To disconnect, call

```
client.close()
```

