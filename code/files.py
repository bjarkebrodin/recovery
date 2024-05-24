from os import listdir as _listdir, sep as _sep, stat as _stat
from os.path import isdir as _isdir, exists as _exists, isfile as _isfile, expandvars as _expandvars, expanduser as _expanduser, islink as _islink, abspath as _abspath
from stat import FILE_ATTRIBUTE_HIDDEN as _HIDDEN_BIT
from inspect import stack as _stack


class Path():
  """
  Make it simpler to navigate and work with the file system the way we want!
  """

  def __init__(self, pathstr):
    path = _expandvars(pathstr)
    path = _expanduser(path)
    path = _abspath(path)

    if not _exists(path): 
      raise FileNotFoundError(f'{path} does not exist!')

    self._parts = path.split(_sep)
    self.parent = _sep.join(self._parts[:-1])
    self.path = _sep.join(self._parts)
    self.name = self._parts[-1]


  # These may change so we need to check each time
  def isdir(self): return _isdir(self.path)
  def isfile(self): return _isfile(self.path)
  def islink(self): return _islink(self.path)

  def ishidden(self): return not self.name.startswith('.') and not bool(_stat(self.path).st_file_attributes & _HIDDEN_BIT)

  def children(self):

    if not self.isdir():
      raise NotADirectoryError(f'{self.path} is not a directory')

    return [Path(_sep.join([self.path, child])) for child in _listdir(self.path)]


  def contents(self):

    if self.isdir():
      raise IsADirectoryError(f'{self.path} is a directory')

    with open(self.path) as f:
      return f.readlines()

  
  def delve(self, include_hidden=False, follow_links=False):

    if not include_hidden and self.ishidden():

      if self.isfile():
        yield self

      if (not self.islink() or follow_links) and self.isdir(): 
        for child in self.children():
          for result in child.delve():
            yield result
      

    




