#!/usr/bin/env python
import subprocess
import sys
import datetime
import time
import cgitb, cgi
import os
import pwd
cgitb.enable()
print("Content-type: text/html\n")
t = time.clock()
arguments = cgi.FieldStorage()
db = arguments["name"].value
env = {'MYSQL_UNIX_PORT':'/var/run/mysqld/mysqld.sock'}
p = subprocess.Popen(['./starstats "MySql ODBC 5.1 Driver" %s -g' % db],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     env=env,
                     shell=True)

(out, err) = p.communicate()
if err is not None and len(err) > 0:
    raise Exception(err)
print(out)

duration = time.clock() - t
print('<div id="footer">Generated by <a href="https://github.com/deweyvm/starstats">starstats</a> on %s in %.4f seconds.</div>' % (time.ctime(), duration))
