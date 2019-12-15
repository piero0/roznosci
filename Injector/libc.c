#include <stdio.h>

void init_debug() {
    printf("init injected\n");
}

void cel_debug(unsigned long cnt) {
    printf("cnt jest: %li\n", cnt);
}
