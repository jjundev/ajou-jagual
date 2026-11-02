#include <stdio.h>
#include <stddef.h>

typedef struct TreeNode {
    int data;
    struct TreeNode *left, *right;
} TreeNode;

int max(int a, int b) { return a > b ? a : b; }

int mystery(TreeNode* p) {
    if (p == NULL) return 0;
    else if (p->left == NULL && p->right == NULL)
        return p->data;
    else
        return max(mystery(p->left), mystery(p->right));
}

int main(void) {
    TreeNode n4 = {4, NULL, NULL}, n2 = {2, NULL, NULL};
    TreeNode n8 = {8, NULL, NULL}, n6 = {6, NULL, NULL};
    TreeNode n5 = {5, &n4, &n2}, n1 = {1, &n8, &n6};
    TreeNode n3 = {3, &n5, &n1};
    printf("p10 mystery(root=3) = %d\n", mystery(&n3));
    return 0;
}
