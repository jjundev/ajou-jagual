#include <stdio.h>
static int read_cell(const int *values, int i, const char *name) {
    printf("R %s.%d\n", name, i);
    return values[i];
}
static void write_cell(int *values, int i, int value, const char *name) {
    values[i] = value;
    printf("W %s.%d %d\n", name, i, value);
}
#define READ(array, i) read_cell(array, i, #array)
#define WRITE(array, i, value) write_cell(array, i, value, #array)
#define SCALAR(name) printf("W f.%s %d\n", #name, name)
#define SWAP_AT(a, b) do { \
    temp = READ(list, a); SCALAR(temp); \
    WRITE(list, a, READ(list, b)); \
    WRITE(list, b, temp); \
} while (0)
int partition(int list[], int left, int right)
{
    int pivot, temp;
    int low, high;

    low = left; SCALAR(low);
    high = right + 1; SCALAR(high);
    pivot = READ(list, left); SCALAR(pivot);
    do {
        do
            { low++; SCALAR(low); }
        while (low <= right && READ(list, low) < pivot);
        do
            { high--; SCALAR(high); }
        while (high >= left && READ(list, high) > pivot);
        if (low < high) SWAP_AT(low, high);
    } while (low < high);

    SWAP_AT(left, high);
    return high;
}

int main(void) {
    int cases[][ 9 ] = {
        {5, 3, 8, 4, 9, 1, 6, 2, 7},
        {5, 5, 8, 5, 9, 1, 6, 5, 7},
        {1, 2, 3, 4, 5, 6, 7, 8, 9},
        {9, 8, 7, 6, 5, 4, 3, 2, 1}
    };
    for (int c = 0; c < 4; c++) {
        printf("CASE %d\n", c);
        int *list = cases[c];
        int q = partition(list, 0, 8); printf("W main.q %d\n", q);
        printf("OUT");
        for (int i = 0; i < 9; i++) printf(" %d", list[i]);
        printf("\n");
    }
}
