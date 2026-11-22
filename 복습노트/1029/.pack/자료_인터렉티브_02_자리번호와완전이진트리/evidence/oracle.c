#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct Node { int key; } Node;

int main(int argc, char **argv) {
    assert(argc == 2);
    Node nodes[8] = {0};
    Node *slot[8] = {NULL};
    int i = 0, gap = 0, n = 0, last = 0, complete = 0, perfect = 0;
    int limit = 7;
    for (int k = 1; k < 8; ++k) nodes[k].key = k;

    if (!strcmp(argv[1], "default")) {
        for (int k = 1; k <= 5; ++k) slot[k] = &nodes[k];
    } else if (!strcmp(argv[1], "gap")) {
        for (int k = 1; k <= 4; ++k) slot[k] = &nodes[k];
        slot[6] = &nodes[6];
    } else if (!strcmp(argv[1], "perfect")) {
        for (int k = 1; k <= 7; ++k) slot[k] = &nodes[k];
    } else if (!strcmp(argv[1], "single")) {
        slot[1] = &nodes[1];
        limit = 1;
    } else {
        assert(!strcmp(argv[1], "empty"));
        limit = 0;
    }

    #define RECORD(line) fprintf(stderr, "%d %d %d %d %d %d %d\n", \
        line, i, gap, n, last, complete, perfect)
    for (i = 1; i <= limit; ++i) {
        RECORD(1);
        RECORD(2);
        if (!slot[i]) {
            if (!gap) gap = i;
            RECORD(3);
            RECORD(4);
            continue;
        }
        printf("%d ", slot[i]->key);
        RECORD(6);
        ++n;
        RECORD(7);
        last = i;
        RECORD(8);
    }
    RECORD(1);
    complete = (n == last);
    RECORD(10);
    perfect = n > 0 && n == limit;
    RECORD(11);
    #undef RECORD
}
