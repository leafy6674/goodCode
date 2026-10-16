from collections import defaultdict


class Solution:
    @staticmethod
    def to_key(s: str) -> tuple[int, ...]:
        freq = [0] * 26
        for ch in s:
            freq[ord(ch) - ord('a')] += 1

        return tuple(freq)

    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        anagram_groups = defaultdict(list)
        for s in strs:
            anagram_groups[self.to_key(s)].append(s)

        return list(anagram_groups.values())
