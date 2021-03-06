#!/usr/bin/env python
#
#
# Copyright (C) 2006 Oracle.	All rights reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a c.of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 021110-1307, USA.
#
# XXX: Future improvements:
#	 
# Program	  : crdel_del_files.py
# Description : will delete the files from generated by the other node in a pair
# Author		  : Marcos E. Matsunaga 
# E-mail		  : Marcos.Matsunaga@oracle.com

#
import os, stat, sys, time, optparse, socket, string, o2tf, pdb, timing, config
#
#pdb.set_trace()
#
#args = sys.argv[1:]
#
#
DEBUGON = os.getenv('DEBUG',0)
#
uname = os.uname()
logfile = config.LOGFILE
#
# MAIN
#
if __name__=='__main__':
	parser = optparse.OptionParser('usage: %prog [-D|--debug] \
		[-l|-logfile logfilename] \
		[-s | --stagedir stagedir] \
		[-h|--help]')
#
	parser.add_option('-D',
		'--debug',
		action="store_true",
		dest='debug',
		default=False,
		help='Turn the debug option on. Default=False.')
#
	parser.add_option('-l', 
		'--logfile',
		dest='logfile',
		type='string',
		help='Logfile used by the process.')
#
	parser.add_option('-s',
		'--stage',
		dest='stagedir',
		type='string',
		help='Directory that will have the workfiles used \
			by the test.')
#
	(options, args) = parser.parse_args()
#	  if len(args) != 0:
#			o2tf.printlog('args left %s' % len(args), logfile, 0, '')
#			parser.error('incorrect number of arguments')
	if options.debug:
		DEBUGON=1
	logfile = options.logfile
	stagedir = options.stagedir
#
# First thing. Check if the dirlist is actually a directory or a file 
# containing the directory list.
#
from os import access, F_OK
if os.access(os.path.join(stagedir, socket.gethostname()+'_D.dat'), F_OK) == 1:
	fd = open(os.path.join(stagedir, socket.gethostname() + '_D.dat'), 'r', 0)
else:
	fd = open(os.path.join(stagedir, socket.gethostbyname(socket.gethostname()) + '_D.dat'), 'r', 0)
dirlist = string.split(fd.read(), ',')
fd.close()
dirlen = len(dirlist)
if DEBUGON:
	o2tf.printlog('crdel_del_files: dirlist = (%s)' % dirlist,
		logfile,
		0,
		'')
	o2tf.printlog('crdel_del_files: stagedir = (%s)' % stagedir,
		logfile,
		0,
		'')
	o2tf.printlog('crdel_del_files: dirlen = (%s)' % dirlen,
		logfile,
		0,
		'')
	o2tf.printlog('crdel_del_files: logfile = (%s)' % logfile,
		logfile,
		0,
		'')
#
for i in range(dirlen):
	o2tf.printlog('crdel_del_files: Removing directory %s.' % 
		dirlist[i],
		logfile,
		0,
		'')
	o2tf.Del(DEBUGON, logfile, dirlist[i], ','.join(dirlist))
#
# Remove the workfile after it is done.
#
if os.access(os.path.join(stagedir, socket.gethostname()), F_OK) == 1:
	os.remove(os.path.join(stagedir, socket.gethostname() + '_D.dat'))
elif os.access(os.path.join(stagedir, socket.gethostbyname(socket.gethostname())), F_OK) == 1:
	os.remove(os.path.join(stagedir, socket.gethostbyname(socket.gethostname()) + '_D.dat'))
sys.exit()
