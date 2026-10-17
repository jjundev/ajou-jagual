/* Harness adds headers, input bounds, buffers and assertions.
   2019 q9 is executed ONLY with its disclosed fourth update corrected to k++.
   The raw UB-prone original is preserved in the cards and is never executed. */
#include <assert.h>
#include <stdio.h>

static int foo(int x, int y) {
    if (x % y == 0) return y;
    else return foo(y, x % y);
}

int main(void) {
    for (int n=1; n<=20; n++) {
        int i,j,p,k,buffer[32][32]={{0}},count=0;
        for(i=0; i<n; i++) {
            for(j=0; j<n; j++) {
                for(p=0; j<i; j++) {
                    for(k=0; k<30; k++) { /* disclosed correction */
                        buffer[i][j]=0;
                        count++;
                    }
                }
            }
        }
        assert(count==30*n*(n-1)/2);
        count=0;
        for(i=1; i<n; i++) {
            for(j=1; j<n; j++) {
                for(p=1; j<=i; j++) {
                    for(k=1; k<30; k++) {
                        buffer[i][j]=1;
                        count++;
                    }
                }
            }
        }
        assert(count==29*n*(n-1)/2);
        (void)p;
        assert(buffer[0][0]==0);
    }
    assert(foo(12,18)==6 && foo(18,12)==6 && foo(1,79)==1);
    puts("PASS C11: bounded original LTK and disclosed corrected 2019 loops n=1..20; positive GCD cases");
    return 0;
}
