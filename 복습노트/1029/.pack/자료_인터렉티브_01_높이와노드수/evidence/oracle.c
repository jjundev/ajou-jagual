#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct Node {
    int key;
    struct Node *left, *right;
} Node;

static int n, h;

static int key(const Node *p) { return p ? p->key : 0; }

static void record(int line, Node *p, int depth) {
    fprintf(stderr, "%d %d %d %d %d\n", line, key(p), depth, n, h);
}

static void visit(Node *p, int d) {
    record(2, p, d);
    if (!p) return;
    ++n;
    record(3, p, d);
    if (d > h) h = d;
    record(4, p, d);
    printf("%d ", p->key);
    record(5, p, d);
    record(6, p->left, d + 1);
    visit(p->left, d + 1);
    record(7, p->right, d + 1);
    visit(p->right, d + 1);
    record(8, p, d);
}

int main(int argc, char **argv) {
    assert(argc == 2);
    Node a[8] = {0};
    for (int i = 1; i <= 7; ++i) a[i].key = i;
    Node *root = a + 1;
    if (!strcmp(argv[1], "default")) {
        a[1].left = a + 2;
        a[1].right = a + 3;
        a[2].left = a + 4;
        a[2].right = a + 5;
        a[3].left = a + 6;
        a[3].right = a + 7;
    } else if (!strcmp(argv[1], "skew7")) {
        for (int i = 1; i < 7; ++i) a[i].left = a + i + 1;
    } else if (!strcmp(argv[1], "skew3")) {
        a[1].left = a + 2;
        a[2].left = a + 3;
    } else if (!strcmp(argv[1], "empty")) {
        root = NULL;
    } else {
        assert(!strcmp(argv[1], "single"));
    }
    record(101, root, 1);
    visit(root, 1);
    record(102, NULL, 0);
}
