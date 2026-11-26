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
static int take_left(int *list, int b1, int b2, int inclusive) {
    int a = READ(list, b1);
    int b = READ(list, b2);
    return inclusive ? a <= b : a < b;
}
void merge(int list[], int left, int mid, int right)
{
    int b1 = left; SCALAR(b1);
    int b2 = mid + 1; SCALAR(b2);
    int sorted[4];
    int index = 0; SCALAR(index);
    while (b1 <= mid && b2 <= right) {
        if (take_left(list, b1, b2, 0)) {
            WRITE(sorted, index, READ(list, b1));
            b1++; SCALAR(b1);
        } else {
            WRITE(sorted, index, READ(list, b2));
            b2++; SCALAR(b2);
        }
        index++; SCALAR(index);
    }
    while (b1 <= mid) {
        WRITE(sorted, index, READ(list, b1));
        b1++; SCALAR(b1);
        index++; SCALAR(index);
    }
    while (b2 <= right) {
        WRITE(sorted, index, READ(list, b2));
        b2++; SCALAR(b2);
        index++; SCALAR(index);
    }
    for (int i = 0; i < index; i++) {
        if (i == 0) SCALAR(i);
        WRITE(list, left + i, READ(sorted, i));
        printf("W f.i %d\n", i + 1);
    }
}

void merge_stable(int list[], int left, int mid, int right)
{
    int b1 = left; SCALAR(b1);
    int b2 = mid + 1; SCALAR(b2);
    int sorted[4];
    int index = 0; SCALAR(index);
    while (b1 <= mid && b2 <= right) {
        if (take_left(list, b1, b2, 1)) {
            WRITE(sorted, index, READ(list, b1));
            b1++; SCALAR(b1);
        } else {
            WRITE(sorted, index, READ(list, b2));
            b2++; SCALAR(b2);
        }
        index++; SCALAR(index);
    }
    while (b1 <= mid) {
        WRITE(sorted, index, READ(list, b1));
        b1++; SCALAR(b1);
        index++; SCALAR(index);
    }
    while (b2 <= right) {
        WRITE(sorted, index, READ(list, b2));
        b2++; SCALAR(b2);
        index++; SCALAR(index);
    }
    for (int i = 0; i < index; i++) {
        if (i == 0) SCALAR(i);
        WRITE(list, left + i, READ(sorted, i));
        printf("W f.i %d\n", i + 1);
    }
}

int main(void) {
    int cases[][ 4 ] = {
        {10, 27, 12, 20},
        {1, 2, 7, 9},
        {2, 5, 2, 3},
        {2, 5, 2, 3}
    };
    for (int c = 0; c < 4; c++) {
        printf("CASE %d\n", c);
        int *list = cases[c];
        if (c == 3) merge_stable(list, 0, 1, 3); else merge(list, 0, 1, 3);
        printf("OUT");
        for (int i = 0; i < 4; i++) printf(" %d", list[i]);
        printf("\n");
    }
}
