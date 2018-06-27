import os

os.system('clear')

uname = raw_input("Escoja la distro Linux utilizada \n[1] - Debian (Ubuntu, Freya, Loky) \n[2] - Fedora (CentOS, RHEL) \n[1 por defecto]: ")
if uname == "2":
    uname == "Fedora"
else:
    uname == "Debian"

data = raw_input("Por favor ingrese el path absoluto al archivo de configuracion [default: /opt/arg2_folder/conf/arg-properties.cfg]: ")
if data == "":
    data = "/opt/arg2_folder/conf/arg-properties.cfg"

if uname == "Debian":
    with open('/etc/init/arg2.conf', 'w') as file_bin:
        raw_binary = '''
#!/bin/bash

description "ARG as a service"
author  "Enzo D. Grosso <enzo@luziasol.com>"

start on runlevel [2345]
stop on runlevel [016]

env ARG_SETTINGS={0}

chdir {1}/src

# NO expect stanza if your script uses python-daemon
exec python initserver.py

# Only turn on respawn after you've debugged getting it to start and stop properly
respawn
'''.format(data, os.getcwd())

        file_bin.write(raw_binary)

        os.system('sudo initctl reload-configuration')

else:

    with open('/etc/init.d/arg2', 'w') as file_bin:

        raw_binary = '''
#!/bin/bash
# chkconfig: 123456 90 10
#
# Author: Enzo D. Grosso <enzo@luziasol.com>

### BEGIN INIT INFO
# Required-Start:   $remote_fs $syslog
# Required-Stop:    $remote_fs $syslog
# Default-Start:    2 3 4 5
# Default-Stop:     0 1 6
# Description:      ARG2 as a service!
### END INIT INFO

workdir={1}/src

start() {
    export ARG_SETTINGS={0}
    /usr/bin/python $workdir/initserver.py > /dev/null 2>&1 &
    echo "ARG2 iniciado"
}

stop() {
    tmp=`ps -ef | grep '{1}/src/initserver.py' | awk '{ print $2 }'`
    pid=`echo $tmp | awk '{ print $1 " " $2}'`
    kill -9 $pid
    echo "ARG2 detenido."
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: arg2 {start|stop|restart}"
    exit 1
esac
exit 0
        '''.format(data, os.getcwd())

        file_bin.write(raw_binary)

        os.system("chmod +x /etc/init.d/arg2")
        os.system("chkconfig --add arg2")

print "ARG2 ya se encuentra instalada como servicio del sistema operativo.\nMuchas gracias por elegir Luzia Soluciones"
