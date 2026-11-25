#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

static void sort(int A[], int n)
{
    int i, j, key;
    for (i=1; i<n; i++) {
        key=A[i];
        for (j=i-1; j>=0 && key < A[j]; j--)
            A[j+1]=A[j];
        A[j+1]=key;
    }
}

int main(void)
{
    int total=0, combinations=1;
    sort(NULL, 0);
    for (int n=0; n<=5; ++n, combinations*=3) {
        for (int trial=0; trial<combinations; ++trial) {
            int values[5]={0}, before[3]={0}, after[3]={0}, digits=trial;
            for (int j=0; j<n; ++j) {
                values[j]=digits%3;
                digits/=3;
                before[values[j]]++;
            }
            sort(values,n);
            for (int j=0; j<n; ++j) {
                assert(j==0 || values[j-1]<=values[j]);
                assert(values[j]>=0 && values[j]<=2);
                after[values[j]]++;
            }
            assert(memcmp(before,after,sizeof before)==0);
            ++total;
        }
    }
    printf("%d arrays (length 0..5, keys 0..2): nondecreasing order and multiset preservation; empty NULL accepted\n",total);
}
