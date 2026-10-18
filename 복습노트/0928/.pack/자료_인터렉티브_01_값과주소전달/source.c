#include <stddef.h>
void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}
int main(void)
{
    int a = 1, b = 2;
    swap(&a, &b);
    return 0;
}