from collections import Counter


class Solution:
    def maxNumberOfBalloons(self, text: str) -> int:
        word_count = Counter("balloon")
        text_count = Counter(text)

        return min(text_count[c] // n for c, n in word_count.items())
