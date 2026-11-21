#include <stdio.h>
#include <string.h>

typedef struct Node {
    int key;
    struct Node *left;
    struct Node *right;
} Node;

static Node intro[] = {{8, intro + 1, intro + 3}, {3, intro + 2, NULL}, {1, NULL, NULL}, {10, NULL, NULL}};
static Node lecture[] = {
    {18, lecture + 1, lecture + 4}, {7, lecture + 2, lecture + 3},
    {3, NULL, NULL}, {12, NULL, NULL}, {26, NULL, lecture + 5},
    {31, lecture + 6, NULL}, {27, NULL, NULL}
};
static Node *nodes;
static size_t length;

static void identify(const Node *p) {
    if (p == NULL) {
        fputs("NULL", stderr);
        return;
    }
    for (size_t i = 0; i < length; ++i) {
        if (p == &nodes[i]) {
            fprintf(stderr, "node-%d", nodes[i].key);
            return;
        }
    }
    fputs("UNKNOWN", stderr);
}

static void record(const char *kind, const char *source, int line, const Node *p, const Node *parent, const char *side) {
    fprintf(stderr, "%s %s %d ", kind, source, line);
    identify(p);
    fputc(' ', stderr);
    identify(parent);
    fprintf(stderr, " %s\n", side);
}

static void inorder(Node *p, const Node *parent, const char *side) {
    record("test", "walk", 2, p, parent, side);
    if (p == NULL) {
        record("return", "walk", 2, p, parent, side);
        return;
    }
    record("call", "walk", 3, p->left, p, "left");
    inorder(p->left, p, "left");
    record("print", "walk", 4, p, parent, side);
    printf("%d ", p->key);
    record("call", "walk", 5, p->right, p, "right");
    inorder(p->right, p, "right");
    record("return", "walk", 6, p, parent, side);
}

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    if (strcmp(argv[1], "default") == 0) {
        nodes = intro;
        length = sizeof intro / sizeof intro[0];
    } else if (strcmp(argv[1], "lecture") == 0) {
        nodes = lecture;
        length = sizeof lecture / sizeof lecture[0];
    } else if (strcmp(argv[1], "empty") != 0) {
        return 2;
    }
    record("call", "driver", 1, nodes, NULL, "root");
    inorder(nodes, NULL, "root");
    return 0;
}
