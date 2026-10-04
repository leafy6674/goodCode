#include <algorithm>
#include <string>

using namespace std;

class Solution {
public:
    string reverseStr(string s, int k) {
        const int n = s.size();

        for (int i = 0; i < n; i += 2 * k) {
            reverse(s, i, min(i + k, n));
        }

        return s;
    }

private:
    // Reverses s[left, right).
    void reverse(string &s, int left, int right) {
        right--;

        while (left < right) {
            swap(s[left], s[right]);
            left++;
            right--;
        }
    }
};
