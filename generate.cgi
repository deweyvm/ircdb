#!/usr/bin/env python
import subprocess
import datetime
env = {'MYSQL_UNIX_PORT':'/var/run/mysqld/mysqld.sock'}
p = subprocess.Popen(["/home/dogue/ircdb/dist/build/ircdb/ircdb", "MySql ODBC 5.1 Driver", "-g"],
                     stdout=subprocess.PIPE,
                     env=env,
                     shell=True)
print("Content-type: text/html\n\n")
t = time.clock()
print(p.stdout.read())
duration = time.clock() - t
print('<div id="footer">Generated by ircdb on %s in %.2f seconds.</div>' % (datetime.datetime.now(), duration))
p.wait()
