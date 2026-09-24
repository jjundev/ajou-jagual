#include <stdio.h>

long long combination(int n, int r) {
  if (r < 0 || r > n)
    return 0;

  if (r > n - r)
    r = n - r;

  long long result = 1;

  for (int i = 1; i <= r; i++) {
    result = result * (n - r + i) / i;
  }

  return result;
}

long long catalan_comb(int x, int y) {
  if (y < 0 || y > x)
    return 0;
  return combination(x + y, y) - combination(x + y, y - 1);
}

int catalan(int x, int y) {
  int result = 0;

  // 금지 좌표인 경우 0
  if (y < 0 || x < y) {
    return 0;
  }

  // 바닥 줄인 경우 1
  if (y == 0) {
    return 1;
  }

  result = catalan(x - 1, y) + catalan(x, y - 1);
  return result;
}

int main(void) {
  int x, y;
  int result;
  long long answer;

  while (1) {
    printf("Enter the values of x and y (or invalid value to exit): ");
    scanf("%d %d", &x, &y);

    if (x < y || y < 0) {
      printf("Invalid input: y cannot be greater than x or y cannot be "
             "negative. Exiting the program.\n");
      break;
    }

    result = catalan(x, y);
    answer = catalan_comb(x, y);
    printf("Catalan number C(%d, %d) using combination formula: %lld\n", x, y,
           answer);
    printf("Catalan number C(%d, %d) using recursion: %d\n", x, y, result);
  }
}
