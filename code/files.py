"""
Fully typed module containing utilities to have more finegrained and OS 
agnostic control of FS navigation without using pwd and cd like operations,
this provides higher flexibility and abstracts away the different logical 
approaches to crawling the file system.
"""


from os import listdir as _listdir, sep as _sep, stat as _stat
from os.path import isdir as _isdir, exists as _exists, isfile as _isfile, expandvars as _expandvars, expanduser as _expanduser, islink as _islink, abspath as _abspath
from stat import FILE_ATTRIBUTE_HIDDEN as _HIDDEN_BIT
from re import match as _match
from typing import List, Iterable
from typing_extensions import Self


class Path():
  """
  Make it simpler to navigate and work with the file system the way we want!
  """

  def __init__(self, pathstr: str):
    path = _expandvars(pathstr)
    path = _expanduser(path)
    path = _abspath(path)

    if not _exists(path): 
      raise FileNotFoundError(f'{path} does not exist! length={len(path)}')

    self._parts = path.split(_sep)
    self.parent = _sep.join(self._parts[:-1])
    self.path = _sep.join(self._parts)
    self.name = self._parts[-1]


  # These may change so we need to check each time
  def isdir(self) -> bool: return _isdir(self.path)
  def isfile(self) -> bool: return _isfile(self.path)
  def islink(self) -> bool: return _islink(self.path)
  def ishidden(self) -> bool: return self.name.startswith('.') or bool(_stat(self.path).st_file_attributes & _HIDDEN_BIT)

  def children(self) -> Iterable[Self]:

    if not self.isdir():
      raise NotADirectoryError(f'{self.path} is not a directory')

    return [Path(_sep.join([self.path, child])) for child in _listdir(self.path)]


  def contents(self) -> Iterable[str]:

    if self.isdir():
      raise IsADirectoryError(f'{self.path} is a directory')

    with open(self.path, 'r', encoding = 'utf-8') as f:
      return f.readlines()

  
  def delve(self, include_hidden: bool = False, follow_links: bool = False, ignore: List[str] = []) -> Iterable[Self]:
    include = not any([_match(i, self.path) is not None for i in ignore])
    follow = (not self.ishidden()) or include_hidden

    if include and follow:

      if self.isfile():
        yield self

      if (not self.islink() or follow_links) and self.isdir(): 
        for child in self.children():
          for result in child.delve(ignore=ignore):
            yield result

