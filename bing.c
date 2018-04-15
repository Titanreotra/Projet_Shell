#include <stdio.h>


void main() {
	char c = getchar();
	int i = 0;

	while(c != EOF ) {
		fputc(c,stderr );
		putchar(c);
		c = getchar();
		i++;
	}
}
