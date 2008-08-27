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
# Program	: run_create_racer.py
# Description 	: Interface to run create_racer. Will validate parameters and
#		properly configure LAM/MPI and start it, before starting
#		the test.
#		This progran will run on each node.
# Author	: Marcos E. Matsunaga 

#
import os, stat, sys, time, optparse, socket, string, o2tf, pdb, random, config
#
#pdb.set_trace()
#
#args = sys.argv[1:]
#
DEBUGON = os.getenv('DEBUG',0)
#
uname = os.uname()
lhostname = str(socket.gethostname())
logfile = config.LOGFILE
iteractions = 10
path = ''
procs = 1
cmd = config.BINDIR+'/create_racer'
#
Usage = '\n	 %prog [-i|--iteractions] \
[-C | --cleanup logfile] \
[-l | --logfile logfile] \
[-n | --nodelist nodelist] \
[-p | --path pathname] \
[-h|--help]'
#
# FUNCTIONS
#
def Cleanup():
	from os import access, F_OK
	for i in range(options.iteractions):
		filename = options.path+'/create_racer:'+str(i).zfill(6)
		if access(filename,F_OK) == 1:
			if DEBUGON:
				o2tf.printlog('create_racer: Removing '+
				'filename (%s)' % filename,
				logfile, 0, '')
			os.system('rm -f %s' % filename)
	sys.exit()
#
# MAIN
#
if __name__=='__main__':
	parser = optparse.OptionParser(usage=Usage)
#
	parser.add_option('-C',
		'--cleanup',
		action="store_true",
		dest='cleanup',
		default=False,
		help='Perform directory cleanup.')
#
	parser.add_option('-i', 
		'--iteractions', 
		dest='iteractions',
		type='int',
		help='Number of iteractions.')
#
	parser.add_option('-l', 
		'--logfile', 
		dest='logfile',
		type='string', 
		help='Logfile used by the process.')
#
	parser.add_option('-n', 
		'--nodelist', 
		dest='nodelist',
		type='string', 
		help='List of nodes where test will run.')
#
	parser.add_option('-p', 
		'--path', 
		dest='path',
		type='string',
		help='pathname used by the test.')
#
	(options, args) = parser.parse_args()
	if len(args) != 0:
		o2tf.printlog('args left %s' % len(args), 
			logfile, 0, '')
		parser.error('incorrect number of arguments')
#
	if options.cleanup and (not options.iteractions or 
		not options.path):
		parser.error('Cleanup options requires path and iteractions.')
#
	if options.iteractions:
		iteractions = options.iteractions
#
	if options.logfile:
		logfile = options.logfile
#
	if options.nodelist:
		nodelist = options.nodelist.split(',')
		nodelen = len(nodelist)
		procs = nodelen
		if nodelen == 1:
			nodelist = nodelist.add(options.nodelist)
		else:
			nodelist = options.nodelist.split(',')
	else:
		if not options.cleanup:
			parser.error('Invalid node list.')

#
	if options.path:
		path = options.path
	else:
		parser.error('Invalid path.')
#
if DEBUGON:
	o2tf.printlog('run_create_racer: main - current directory %s' % 
		os.getcwd(), logfile, 0, '')
	o2tf.printlog('run_create_racer: main - cmd = %s' % cmd,
		logfile, 0, '')
#
if options.cleanup:
	Cleanup()
o2tf.StartMPI(DEBUGON, options.nodelist, logfile)
#
ret = o2tf.mpi_run(DEBUGON, procs, 
	str('%s -i %s %s 2>&1 | tee -a %s' % (cmd, 
	options.iteractions, 
	options.path, 
	options.logfile)), 
	options.nodelist, 
	options.logfile)
#
if not ret:
	o2tf.printlog('run_create_racer: main - execution successful.',
		logfile, 0, '')
Cleanup()