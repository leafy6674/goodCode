#include <algorithm>
#include <string>

using namespace std;

class Solution {
public:
    string reverseWords(string s) {
        removeExtraSpaces(s);
        reverse(s.begin(), s.end());
        reverseEachWord(s);
        return s;
    }

private:
    // drop leading/trailing spaces and collapse runs of spaces into one
    void removeExtraSpaces(string& s) {
        int writePos = 0, n = s.size();
        for (int readPos = 0; readPos < n; ++readPos) {
            if (s[readPos] != ' ') {
                if (writePos != 0) s[writePos++] = ' ';
                while (readPos < n && s[readPos] != ' ') s[writePos++] = s[readPos++];
            }
        }
        s.erase(s.begin() + writePos, s.end());
    }

    void reverseEachWord(string& s) {
        int wordStart = 0, wordEnd = 0, n = s.size();
        while (wordStart < n) {
            wordStart = wordEnd;
            while (wordStart < n && s[wordStart] == ' ') {
                wordStart++;
            }
            wordEnd = wordStart;
            while (wordEnd < n && s[wordEnd] != ' ') {
                wordEnd++;
            }
            reverse(s.begin() + wordStart, s.begin() + wordEnd);
        }
    }
};
