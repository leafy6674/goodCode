class Solution {
public:
    int maxNumberOfBalloons(string text) {
        string word = "balloon";
        vector<int> wordCount(26, 0), textCount(26, 0);
        for (char c : word) wordCount[c - 'a']++;
        for (char c : text) textCount[c - 'a']++;

        int res = INT_MAX;
        for (int i = 0; i < 26; i++)
            if (wordCount[i] > 0)
                res = min(res, textCount[i] / wordCount[i]);

        return res;
    }
};
