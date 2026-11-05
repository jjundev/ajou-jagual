#include <stdio.h>
#include <stdlib.h>
typedef struct TreeNode {int key; struct TreeNode *left,*right;} TreeNode;
TreeNode *search(TreeNode *node,int key) {
    if(node==NULL) return NULL;
    if(key==node->key) return node;
    if(key<node->key) return search(node->left,key);
    return search(node->right,key);
}
int insert_node(TreeNode **root,TreeNode *z) {
    TreeNode *p=NULL,*t=*root;
    while(t!=NULL) {
        if(z->key==t->key) return 0;
        p=t;
        if(z->key<p->key) t=p->left; else t=p->right;
    }
    if(p==NULL) *root=z;
    else if(z->key<p->key) p->left=z;
    else p->right=z;
    return 1;
}
int main(void) {
    TreeNode n3={3,NULL,NULL},n12={12,NULL,NULL},n7={7,&n3,&n12};
    TreeNode n27={27,NULL,NULL},n31={31,&n27,NULL},n26={26,NULL,&n31};
    TreeNode n18={18,&n7,&n26},*root=&n18;
    printf("search12=%d search20=%s\n",search(root,12)->key,search(root,20)==NULL?"NULL":"found");
    TreeNode n9={9,NULL,NULL};
    printf("insert9=%d\n",insert_node(&root,&n9));
    printf("parent12.left=%d\n",n12.left->key);
    TreeNode dup={9,NULL,NULL};
    printf("duplicate9=%d\n",insert_node(&root,&dup));
    TreeNode empty_node={9,NULL,NULL},*empty=NULL;
    int ok=insert_node(&empty,&empty_node);
    printf("empty_insert=%d root=%d\n",ok,empty->key);
    return 0;
}
