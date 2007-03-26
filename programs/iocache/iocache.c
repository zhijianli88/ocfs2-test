/* -*- mode: c; c-basic-offset: 8; -*-
 * vim: noexpandtab sw=8 ts=8 sts=0:
 *
 * iocache.c - Test libocfs2 io cache.
 *
 * The program is simple.
 *
 * 1) Read the original blocks off.
 * 2) Initialize the cache.
 * 3) Read the blocks again, compare against the originals.
 * 4) Read again, expecting the cache to return them.  Compare.
 * 5) Write a pattern to the blocks.
 * 6) Read them again, expecting the pattern.
 * 7) Start a child process.
 * 8)           The child reads the blocks, expecting the pattern.
 * 9)           The child writes a new pattern to the blocks.
 * 10) The parent reads the blocks again.  Because it has a cache, it
 *     should still see the old pattern.
 * 11) Write the original blocks back.
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <inttypes.h>

#include <ocfs2/ocfs2.h>


#define NUM_BLOCKS 10
#define BLOCKSIZE 4096
#define PATTERN1 "a"
#define PATTERN2 "b"

char *progname;
static int number_of_blocks = NUM_BLOCKS;
static uint64_t blknos[NUM_BLOCKS];
static int blocksize = BLOCKSIZE;
static char *original_blocks[NUM_BLOCKS];
static char *pattern_blocks[NUM_BLOCKS];
static char *working_blocks[NUM_BLOCKS];
static io_channel *channel;


static void usage(int rc)
{
	fprintf(stderr, "Usage: %s <filename>\n", progname);
	exit(rc);
}

static int open_device(const char *dev)
{
	errcode_t ret;

	ret = io_open(dev, OCFS2_FLAG_RW, &channel);
	if (ret) {
		com_err(progname, ret, "while opening file \"%s\"", dev);
		return -ENXIO;
	}

	io_set_blksize(channel, blocksize);

	return 0;
}

static void finalize(void);
static int initialize(int argc, char *argv[])
{
	int rc, i;
	errcode_t ret = 0;
	progname = argv[0];

	if (argc != 2)
		usage(-EINVAL);
	if (!strcmp(argv[1], "-h") ||
	    !strcmp(argv[1], "-?") ||
	    !strcmp(argv[1], "--help"))
		usage(0);
	if (argv[1][0] == '-')
		usage(-EINVAL);

	rc = open_device(argv[1]);
	if (rc)
		goto out;

	/* open_device() set our blocksize */
	for (i = 0; i < number_of_blocks; i++) {
		ret = ocfs2_malloc_block(channel, &original_blocks[i]);
		if (ret)
			goto out;
		ret = ocfs2_malloc_block(channel, &pattern_blocks[i]);
		if (ret)
			goto out;
		ret = ocfs2_malloc_block(channel, &working_blocks[i]);
		if (ret)
			goto out;
	}

	/*
	 * XXX: Make this smarter :-)
	 * This loop just takes the number_of_blocks blocks starting at
	 * block 20.  It really should be randomly picking blocks all
	 * over the disk.
	 */
	for (i = 0; i < number_of_blocks; i++)
		blknos[i] = i + 20;

out:
	if (ret) {
		com_err(progname, ret, "while initializing the test");
		rc = -ENOMEM;

		finalize();
	}

	return rc;
}

static int step1(void)
{
	int i, failed = 0;
	errcode_t ret;

	for (i = 0; !failed && (i < number_of_blocks); i++) {
		ret = io_read_block(channel, blknos[i], 1, 
				    original_blocks[i]);
		if (ret) {
			failed = 1;
			com_err(progname, ret,
				"while reading block %"PRIu64, blknos[i]);
		}
	}

	return failed;
}

static int step2(void)
{
	int failed = 0;
	errcode_t ret;

	ret = io_init_cache(channel, number_of_blocks);
	if (ret) {
		com_err(progname, ret, "while initializing cache");
		failed = 1;
	}

	return failed;
}

static int step3(void)
{
	int i, failed = 0;
	errcode_t ret;

	for (i = 0; !failed && (i < number_of_blocks); i++) {
		ret = io_read_block(channel, blknos[i], 1, 
				    working_blocks[i]);
		if (ret) {
			failed = 1;
			com_err(progname, ret,
				"while reading block %"PRIu64, blknos[i]);
		}
	}

	for (i = 0; !failed && (i < number_of_blocks); i++) {
		if (memcmp(original_blocks[i], working_blocks[i],
			   io_get_blksize(channel))) {
			failed = 1;
		}
	}

	return failed;
}

static int step11(void)
{
	int i, failed = 0;
	errcode_t ret;

	/* Drop the cache so writeback is through the sync codepaths */
	io_destroy_cache(channel);

	for (i = 0; i < number_of_blocks; i++) {
		ret = io_write_block(channel, blknos[i], 1,
				     original_blocks[i]);
		if (ret) {
			failed = 1;
			com_err(progname, ret,
				"while writing back original block %"PRIu64,
				blknos[i]);
		}
	}

	return failed;
}

static void finalize(void)
{
	int i;

	for (i = 0; i < number_of_blocks; i++) {
		ocfs2_free(&original_blocks[i]);
		ocfs2_free(&pattern_blocks[i]);
		ocfs2_free(&working_blocks[i]);

		io_close(channel);
	}
}

int main(int argc, char *argv[])
{
	int failed = 0;
	int rc;

	rc = initialize(argc, argv);

	failed += step1();
	failed += step2();
	failed += step3();

	failed += step11();

	finalize();

	return rc;
}
