TOPDIR = ../..

include $(TOPDIR)/Preamble.make

TESTS = flock_unit_test

CC = $(MPICC)

CFLAGS = -O2 -Wall -g

SOURCES = flock_unit_test.c
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))

DIST_FILES = $(SOURCES)

BIN_PROGRAMS = flock_unit_test

BIN_EXTRA = run_flock_unit_test.py concurrent_flock_test.pl

flock_unit_test: $(OBJECTS)
	$(LINK)

include $(TOPDIR)/Postamble.make
