#include <iostream>
#include <string>
using namespace std;

class Solution {
public:
    string replaceNumber(string s) {
        int digitCount = 0;
        for (char ch : s) {
            if (ch >= '0' && ch <= '9') {
                digitCount++;
            }
        }

        // 每个数字变成 6 个字符，多出 5 个
        int oldSize = s.size();
        s.resize(oldSize + digitCount * 5);

        // 从后往前填充，避免覆盖还没处理的字符
        for (int i = oldSize - 1, j = s.size() - 1; i >= 0; i--) {
            if (s[i] >= '0' && s[i] <= '9') {
                s[j--] = 'r';
                s[j--] = 'e';
                s[j--] = 'b';
                s[j--] = 'm';
                s[j--] = 'u';
                s[j--] = 'n';
            } else {
                s[j--] = s[i];
            }
        }

        return s;
    }
};

int main() {
    string s;
    while (cin >> s) {
        cout << Solution().replaceNumber(s) << endl;
    }
    return 0;
}
