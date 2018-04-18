#include <stdio.h>


void main() {
	char c = getchar();
	int i = 0;

	while(c != EOF ) {
		fputc(c,stderr );
		fputc('z',stdout);
		c = getchar();
		i++;
	}
}
