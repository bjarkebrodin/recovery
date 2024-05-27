from typing import List, TypeVar

T = TypeVar('T')
def flatten(l: List[List[T]]) -> List[T]:
  return [x for y in l for x in y]
