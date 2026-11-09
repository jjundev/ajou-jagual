/* S8 p13 delete_max_heap, literal C11 translation + fixed variant. */
#include <stdio.h>
#include <string.h>
#define MAX_ELEMENT 200
#define PARENT(i) ((i) / 2)
#define CHILD(i) ((i) * 2)

static int heap_size;

static void swap(int *x, int *y) { int t = *x; *x = *y; *y = t; }

static int delete_max_heap(int A[], int fixed) {
    int item = A[1];
    A[1] = A[heap_size];
    heap_size = heap_size - 1;
    int i = 2, largest;
    while (i <= heap_size) {
        if (!fixed) {
            if (i < heap_size && A[i] > A[i + 1]) largest = i; else largest = i + 1;
        } else {
            if (i < heap_size && A[i + 1] > A[i]) largest = i + 1; else largest = i;
        }
        if (A[PARENT(largest)] > A[largest]) { printf("    i=%d largest=%d break\n", i, largest); break; }
        printf("    i=%d largest=%d swap A[%d]<->A[%d]\n", i, largest, PARENT(largest), largest);
        swap(&A[PARENT(largest)], &A[largest]);
        i = CHILD(largest);
    }
    return item;
}

static void run(const char *tag, const int *init, int n, int fixed) {
    int A[MAX_ELEMENT];
    memset(A, 0, sizeof A);
    for (int k = 0; k < n; k++) A[k + 1] = init[k];
    heap_size = n;
    printf("%s (%s)\n", tag, fixed ? "fixed" : "literal");
    int item = delete_max_heap(A, fixed);
    printf("    return=%d A[1..%d]=", item, heap_size);
    for (int k = 1; k <= heap_size; k++) printf("%d ", A[k]);
    int ok = 1;
    for (int k = 2; k <= heap_size; k++) if (A[k] > A[PARENT(k)]) ok = 0;
    printf("| max-heap=%s | A[%d](stale)=%d\n", ok ? "yes" : "no", heap_size + 1, A[heap_size + 1]);
}

int main(void) {
    const int a[] = {9, 7, 6, 5, 4, 3, 2, 2, 1, 3};
    const int b[] = {50, 40, 30, 20, 10};
    run("(a)", a, 10, 0);
    run("(a)", a, 10, 1);
    run("(b)", b, 5, 0);
    run("(b)", b, 5, 1);
    return 0;
}
