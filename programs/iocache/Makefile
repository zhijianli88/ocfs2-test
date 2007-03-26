TOPDIR = ../..

include $(TOPDIR)/Preamble.make

TESTS = iocache

CFLAGS = -O2 -Wall -g $(OCFS2_CFLAGS)

SOURCES = iocache.c

DIST_FILES = $(SOURCES)

BIN_PROGRAMS = iocache

iocache: iocache.o
	$(LINK) $(OCFS2_LIBS)

include $(TOPDIR)/Postamble.make
