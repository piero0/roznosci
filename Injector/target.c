#include <stdio.h>
#include <time.h>

void wstrzyk() {
    printf("wstrzyk\n");
}

void init() {
    printf("init\n");
}

void cel(unsigned long cnt) {
    printf("cnt: %li\n", cnt);
}

int main() {
    time_t cur = 0, prev = time(0);
    unsigned long cnt = 0;

    init();

    cel(cnt);

    while(1) {
        cur = time(0);
        if(cur - prev >= 1) {
            //printf("%i\n", cnt);
            cel(cnt);
            prev = cur;
        }
        cnt++;
    }
}