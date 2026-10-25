#include <vector>

using namespace std;

class Solution {
public:
    vector<vector<int>> combine(int n, int k) {
        vector<vector<int>> result;
        vector<int> path;
        backtrack(1, n, k, path, result);
        return result;
    }

private:
    void backtrack(int start, int n, int k, vector<int>& path, vector<vector<int>>& result) {
        if ((int)path.size() == k) {
            result.push_back(path);
            return;
        }

        // Stop once there aren't enough numbers left to fill the combination.
        for (int i = start; i <= n - (k - (int)path.size()) + 1; ++i) {
            path.push_back(i);
            backtrack(i + 1, n, k, path, result);
            path.pop_back();
        }
    }
};
