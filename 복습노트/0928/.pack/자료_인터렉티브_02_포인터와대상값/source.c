#include <stddef.h>
void change(int *p)
{
    *p = 20;
    p = NULL;
}
int main(void)
{
    int a = 10;
    int *q = &a;
    change(q);
    return 0;
}