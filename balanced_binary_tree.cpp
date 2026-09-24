#include <algorithm>
#include <cstdlib>

using namespace std;

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

class Solution {
 public:
  bool isHeightBalanced(TreeNode* root) {
    bool balanced = true;
    maxDepth(root, balanced);
    return balanced;
  }

 private:
  // Returns the depth of node and sets balanced to false once any subtree is
  // unbalanced; after that, the remaining nodes are skipped.
  int maxDepth(TreeNode* node, bool& balanced) {
    if (node == nullptr || !balanced)
      return 0;
    const int leftDepth = maxDepth(node->left, balanced);
    const int rightDepth = maxDepth(node->right, balanced);
    if (abs(leftDepth - rightDepth) > 1)
      balanced = false;
    return max(leftDepth, rightDepth) + 1;
  }
};
