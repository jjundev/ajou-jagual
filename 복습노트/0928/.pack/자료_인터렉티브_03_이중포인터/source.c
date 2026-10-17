#include <stddef.h>
void redirect(int **pp, int *next)
{
    *pp = next;
}
int main(void)
{
    int a = 10, b = 20;
    int *q = &a;
    redirect(&q, &b);
    return 0;
}