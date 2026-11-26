void merge(int list[], int left, int mid, int right)
{
    int b1 = left;
    int b2 = mid + 1;
    int sorted[4];
    int index = 0;
    while (b1 <= mid && b2 <= right) {
        if (list[b1] < list[b2]) {
            sorted[index] = list[b1];
            b1++;
        } else {
            sorted[index] = list[b2];
            b2++;
        }
        index++;
    }
    while (b1 <= mid) {
        sorted[index] = list[b1];
        b1++;
        index++;
    }
    while (b2 <= right) {
        sorted[index] = list[b2];
        b2++;
        index++;
    }
    for (int i = 0; i < index; i++)
        list[left + i] = sorted[i];
}
