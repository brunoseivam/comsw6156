#include <stdio.h>

typedef struct msgBuff {
    char message[128];
} TAB_BUFFER;

int main(void) {
    TAB_BUFFER buf;
    char *type = "dummy";
    char *pdbentry = "dummy";

    // Write >128 chars
    char *pfield_name = 
        "123456789012345678901234567890"
        "123456789012345678901234567890"
        "123456789012345678901234567890"
        "123456789012345678901234567890"
        "123456789012345678901234567890";

    sprintf(buf.message, "%-4sL %s %s", pfield_name,
        type, pdbentry
    );

    return 0;
}