class Solution:
  def twoSum(self, nums: list[int], target: int) -> list[int]:
    seen = dict()

    for i, num in enumerate(nums):
      compliment = target - num
      if compliment in seen:
        return [i, seen[compliment]]
      seen[num] = i

    return []
