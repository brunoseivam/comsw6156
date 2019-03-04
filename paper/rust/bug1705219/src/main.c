#include <stdio.h>

char *get_str(void) {
    char s[64] = "dummy";
    return s;
}

int main(void) {
    char *s = get_str();
    printf("%s\n", s);
    return 0;
}