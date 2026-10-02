#include <unordered_set>
using namespace std;

class Solution {
private:
  int digitSquareSum(int n) {
    int sum = 0;
    while (n > 0) {
      int last = n % 10;
      sum += last * last;
      n /= 10;
    }
    return sum;
  }

public:
  bool isHappy(int n) {
    unordered_set<int> seen;
    while (n != 1) {
      if (!seen.insert(n).second)
        return false;  // revisited a number: stuck in a cycle
      n = digitSquareSum(n);
    }
    return true;
  }
};
