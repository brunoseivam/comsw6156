#include <stdio.h>

struct Dummy {
    int d;
    Dummy(int d):d(d) {}
};

int main(void) {
    Dummy *dummy = new Dummy(42);
    delete dummy;
    printf("%d\n", dummy->d);
    return 0;
}