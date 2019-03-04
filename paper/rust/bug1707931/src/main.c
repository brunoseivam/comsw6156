#include <stdio.h>

int main(void) {
    unsigned int u = 42;
    if (u < 0)
        printf("Should never happen");

    int i = -42;
    unsigned int u2 = i;
    if (u2 < 0)
        printf("Should never happen");

    return 0;
}