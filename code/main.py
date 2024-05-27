from typing import List, TypeVar, Set, Callable
from files import Path
from re import match
from os import sep


###########################################################################################
### JS UTILS: TODO: MOVE INTO OWN FILE

# Inspired by Mircea Lungo's code found at:
# https://colab.research.google.com/drive/1oe_TV7936Zmmzbbgq8rzqFpxYPX7SQHP#scrollTo=0ruTtX88Tb-w
# accessed at 18:38 CET on 27-05-2024
def extract_module(file: Path) -> str:
  return file.path.split('src\\')[-1].replace('\\','.').replace('.js','').replace('.sc','')

T = TypeVar('T')
def flatten(l: List[List[T]]) -> List[T]:
  return [x for y in l for x in y]

def is_local_import(s: str) -> bool: 
  return '.' in s

def to_module_path_from_relative(file: Path) -> Path: 
  return lambda s: Path(sep.join(file.path.split(sep)[:-1]) + sep + s.replace('/', sep).replace('.js', '') + '.js')

def extract_js_imports(file: Path, ignore: List[str] = []) -> List[str]:

  def _extractor(linefilter: Callable[[str], bool], linemapping: Callable[[str], str]) -> Callable[[], str]:
    def __result_extractor():
      return list(
        map(extract_module,
        map(to_module_path_from_relative(file),
        filter(is_local_import,
        map(linemapping,
        filter(linefilter,
        file.contents()))))))
    
    return __result_extractor

  # Gets only singleline from imports such as "import component from 'module';"
  _from_import_linefilter = lambda line: line.startswith('import') and ';' in  line and 'from' in line and not any([match(i, line) is not None for i in ignore])
  _from_import_linemapping = lambda line: line.replace(';', '').replace('"', '').strip().replace('\n', '').split('from')[-1].strip()
  _from_import_extractor = _extractor(_from_import_linefilter, _from_import_linemapping)
    
  # Gets only singleline flat imports such as "import './module';"
  _flat_import_linefilter = lambda line: line.startswith('import') and ';' in line and 'from' not in line and not any([match(i, line) is not None for i in ignore])
  _flat_import_linemapping = lambda line: line.replace(';', '').replace('"', '').strip().replace('\n', '').split(' ')[-1].strip()
  _flat_import_extractor = _extractor(_flat_import_linefilter, _flat_import_linemapping)

  from_imports = _from_import_extractor()
  flat_imports = _flat_import_extractor()
    
  return from_imports + flat_imports
###########################################################################################


def main():

  # Can also just filter the path on only js afterwards but this speeds up crawl :)
  ignore_files: List[str] = [
    '.*node_modules.*',
    '.*tex.*',
    '.*notes.*',
    '.*public.*',
    '.*.json',
  ]

  ignore_imports: List[str] = [
    ".*.css",
    ".*.json",
  ]


  codefiles: List[Path] = list(Path('./src').delve(ignore=ignore_files))
  modules: Set[str] = set(map(extract_module, codefiles))
  outrefs = None
  increfs = None

  for f in codefiles:
    print(extract_module(f), '<-', extract_js_imports(f, ignore=ignore_imports))

  # todo: abstract modules into a tree to work with abstraction hierarchy
  # todo: look at truck
  # todo: can generate UML by using semantic analysis, find libs for this!



if __name__ == '__main__': main()
