#include <ranges>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

class Solution {
public:
  u32string freqKey(const string &str) {
    u32string freq(26, '\0');
    for (char c : str)
      freq[c - 'a']++;

    return freq;
  }

  vector<vector<string>> groupAnagrams(vector<string> &strs) {
    unordered_map<u32string, vector<string>> groups;
    for (string &str : strs) {
      groups[freqKey(str)].push_back(str);
    }

    auto res = groups | views::values | views::as_rvalue;

    return {res.begin(), res.end()};
  }
};
