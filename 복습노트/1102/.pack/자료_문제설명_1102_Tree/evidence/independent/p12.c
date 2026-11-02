#include <stdio.h>
#include <stddef.h>

typedef struct TreeNode {
    char data;
    struct TreeNode *left, *right;
} TreeNode;

int max(int a, int b) { return a > b ? a : b; }

int get_node_count(TreeNode *node)
{
    int count=0;
    if( node != NULL )
        count = 1 + get_node_count(node->left)+
                get_node_count(node->right);
    return count;
}

int get_height(TreeNode *node)
{
    int height=0;
    if( node != NULL )
        height = 1 + max(get_height(node->left),
                         get_height(node->right));
    return height;
}

/* (c) 확인용: +1 을 뺀 변형 */
int get_height_no_plus1(TreeNode *node)
{
    int height=0;
    if( node != NULL )
        height = max(get_height_no_plus1(node->left),
                     get_height_no_plus1(node->right));
    return height;
}

int main(void) {
    /* L1, L2, L3 는 char 한 글자라 '1','2','3' 으로 저장 */
    TreeNode L1 = {'1', NULL, NULL}, L2 = {'2', NULL, NULL}, L3 = {'3', NULL, NULL};
    TreeNode X = {'X', &L1, &L2}, Y = {'Y', &L3, NULL};
    TreeNode R = {'R', &X, &Y};
    printf("get_node_count(X) = %d\n", get_node_count(&X));
    printf("get_node_count(Y) = %d\n", get_node_count(&Y));
    printf("get_node_count(R) = %d\n", get_node_count(&R));
    printf("get_height(R) = %d\n", get_height(&R));
    printf("get_height_no_plus1(R) = %d, (X) = %d, (L1) = %d\n",
           get_height_no_plus1(&R), get_height_no_plus1(&X), get_height_no_plus1(&L1));
    return 0;
}
