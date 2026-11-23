enum { N = 3 };

void degrees(int m[N][N], int v, int sum[2])
{
    for (int i = 0; i < N; ++i)
        sum[0] += m[v][i];

    for (int i = 0; i < N; ++i)
        sum[1] += m[i][v];
}
