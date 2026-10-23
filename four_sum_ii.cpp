#include <unordered_map>
#include <vector>

using namespace std;

class Solution {
public:
    int fourSumCount(vector<int>& nums1, vector<int>& nums2,
                     vector<int>& nums3, vector<int>& nums4) {
        unordered_map<int, int> pairSums;

        for (int a : nums1) {
            for (int b : nums2) {
                ++pairSums[a + b];
            }
        }

        int count = 0;
        for (int c : nums3) {
            for (int d : nums4) {
                auto it = pairSums.find(-(c + d));
                if (it != pairSums.end()) {
                    count += it->second;
                }
            }
        }

        return count;
    }
};
