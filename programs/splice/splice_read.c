/* splice_read.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <sys/stat.h>

int main(int argc, char *argv[])
{
	int fd;
	int slen;
	struct stat st;
	int size;

	if (argc < 2) {
		printf("Usage: ./splice_read out | cat\n");
		exit(-1);
	}

	fd = open(argv[1], O_RDONLY, 0644);
	if (fd == -1) {
		printf("open file failed.\n");
		exit(-1);
	}
	stat(argv[1], &st);
	size = st.st_size;

	while (size > 0) {
		slen = splice(fd, NULL, STDOUT_FILENO, NULL, size, 0);
		if (slen < 0) {
			fprintf(stderr, "splice failed.\n");
			break;
		} else {
			fprintf(stderr, "spliced length = %d\n",slen);
			size -= slen;
		}
	}
	close(fd);
	if (slen <0)
		exit(-1);

	return 0;
}

