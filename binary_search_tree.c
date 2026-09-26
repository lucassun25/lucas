#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 定义二叉搜索树节点结构
typedef struct TreeNode {
    int data;
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

// 创建新节点
TreeNode* createNode(int data) {
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (node == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }
    node->data = data;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// 插入节点
TreeNode* insert(TreeNode* root, int data) {
    if (root == NULL) {
        return createNode(data);
    }
    
    if (data < root->data) {
        root->left = insert(root->left, data);
    } else if (data > root->data) {
        root->right = insert(root->right, data);
    }
    // 如果data == root->data，则不插入重复值
    
    return root;
}

// 查找节点（中序遍历找最小值）
TreeNode* findMin(TreeNode* node) {
    if (node == NULL) {
        return NULL;
    }
    while (node->left != NULL) {
        node = node->left;
    }
    return node;
}

// 删除节点
TreeNode* delete(TreeNode* root, int data) {
    if (root == NULL) {
        return NULL;
    }
    
    if (data < root->data) {
        root->left = delete(root->left, data);
    } else if (data > root->data) {
        root->right = delete(root->right, data);
    } else {
        // 找到了要删除的节点
        
        // 情况1：节点是叶子节点
        if (root->left == NULL && root->right == NULL) {
            free(root);
            return NULL;
        }
        
        // 情况2：节点只有右子树
        if (root->left == NULL) {
            TreeNode* temp = root->right;
            free(root);
            return temp;
        }
        
        // 情况3：节点只有左子树
        if (root->right == NULL) {
            TreeNode* temp = root->left;
            free(root);
            return temp;
        }
        
        // 情况4：节点有两个子树
        // 找到右子树中的最小节点（中序后继）
        TreeNode* minRight = findMin(root->right);
        root->data = minRight->data;
        root->right = delete(root->right, minRight->data);
    }
    
    return root;
}

// 搜索节点
TreeNode* search(TreeNode* root, int data) {
    if (root == NULL) {
        return NULL;
    }
    
    if (data == root->data) {
        return root;
    } else if (data < root->data) {
        return search(root->left, data);
    } else {
        return search(root->right, data);
    }
}

// 中序遍历（左-根-右）- 升序输出
void inorderTraversal(TreeNode* root) {
    if (root == NULL) {
        return;
    }
    inorderTraversal(root->left);
    printf("%d ", root->data);
    inorderTraversal(root->right);
}

// 前序遍历（根-左-右）
void preorderTraversal(TreeNode* root) {
    if (root == NULL) {
        return;
    }
    printf("%d ", root->data);
    preorderTraversal(root->left);
    preorderTraversal(root->right);
}

// 后序遍历（左-右-根）
void postorderTraversal(TreeNode* root) {
    if (root == NULL) {
        return;
    }
    postorderTraversal(root->left);
    postorderTraversal(root->right);
    printf("%d ", root->data);
}

// 释放整棵树的内存
void freeTree(TreeNode* root) {
    if (root == NULL) {
        return;
    }
    freeTree(root->left);
    freeTree(root->right);
    free(root);
}

// 计算树的高度
int getHeight(TreeNode* root) {
    if (root == NULL) {
        return 0;
    }
    int leftHeight = getHeight(root->left);
    int rightHeight = getHeight(root->right);
    return (leftHeight > rightHeight ? leftHeight : rightHeight) + 1;
}

// 测试程序
int main() {
    TreeNode* root = NULL;
    
    printf("=== Binary Search Tree Operations ===\n\n");
    
    // 插入数据
    printf("Inserting values: 50, 30, 70, 20, 40, 60, 80, 10, 25, 65\n");
    root = insert(root, 50);
    root = insert(root, 30);
    root = insert(root, 70);
    root = insert(root, 20);
    root = insert(root, 40);
    root = insert(root, 60);
    root = insert(root, 80);
    root = insert(root, 10);
    root = insert(root, 25);
    root = insert(root, 65);
    
    printf("\nInorder Traversal (Ascending): ");
    inorderTraversal(root);
    printf("\n");
    
    printf("Preorder Traversal: ");
    preorderTraversal(root);
    printf("\n");
    
    printf("Postorder Traversal: ");
    postorderTraversal(root);
    printf("\n");
    
    printf("Tree Height: %d\n", getHeight(root));
    
    // 搜索测试
    printf("\n--- Search Tests ---\n");
    int searchValue = 25;
    if (search(root, searchValue) != NULL) {
        printf("Value %d found in tree\n", searchValue);
    } else {
        printf("Value %d not found in tree\n", searchValue);
    }
    
    searchValue = 100;
    if (search(root, searchValue) != NULL) {
        printf("Value %d found in tree\n", searchValue);
    } else {
        printf("Value %d not found in tree\n", searchValue);
    }
    
    // 删除测试
    printf("\n--- Delete Operations ---\n");
    printf("Deleting leaf node (10): ");
    root = delete(root, 10);
    inorderTraversal(root);
    printf("\n");
    
    printf("Deleting node with one child (30): ");
    root = delete(root, 30);
    inorderTraversal(root);
    printf("\n");
    
    printf("Deleting node with two children (50): ");
    root = delete(root, 50);
    inorderTraversal(root);
    printf("\n");
    
    printf("Final Tree Height: %d\n", getHeight(root));
    
    // 释放内存
    freeTree(root);
    printf("\nMemory freed successfully\n");
    
    return 0;
}
