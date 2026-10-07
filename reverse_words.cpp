#include <algorithm>
#include <string>

using namespace std;

// Reverses the order of dot-separated words in place, collapsing repeated
// dots and dropping leading/trailing ones: "..geeks..for.geeks." -> "geeks.for.geeks"
string reverseWords(string s) {
    // reverse the whole string
    reverse(s.begin(), s.end());

    int n = s.size();
    int i = 0;
    for (int l = 0; l < n; ++l) {
        if (s[l] != '.') {
            // separate from the previous word
            if (i != 0) s[i++] = '.';

            // copy the word to the write position
            int r = l;
            while (r < n && s[r] != '.') s[i++] = s[r++];

            // reverse the word back to its original spelling
            reverse(s.begin() + i - (r - l), s.begin() + i);

            // move to the next word
            l = r;
        }
    }
    s.erase(s.begin() + i, s.end());
    return s;
}
