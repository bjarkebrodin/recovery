from typing import List, Callable
from files import Path
from re import match
from os import sep

# Inspired by Mircea Lungo's code found at:
# https://colab.research.google.com/drive/1oe_TV7936Zmmzbbgq8rzqFpxYPX7SQHP#scrollTo=0ruTtX88Tb-w
# accessed at 18:38 CET on 27-05-2024
def extract_module(file: Path) -> str:
  return file.path.split('src\\')[-1].replace('\\','.').replace('.js','').replace('.sc','')

def is_local_import(s: str) -> bool: 
  return '.' in s

def to_module_path_from_relative(file: Path) -> Path: 
  return lambda s: Path(sep.join(file.path.split(sep)[:-1]) + sep + s.replace('/', sep).replace('.js', '') + '.js')

def extract_js_imports(file: Path, ignore: List[str] = []) -> List[str]:

  def _extractor(linefilter: Callable[[str], bool], linemapping: Callable[[str], str]) -> Callable[[], List[str]]:
    def __result_extractor() -> List[str]:
      return list(
        map(extract_module,
        map(to_module_path_from_relative(file),
        filter(is_local_import,
        map(linemapping,
        filter(linefilter,
        file.contents()))))))
    
    return __result_extractor


  # Gets only singleline from imports such as "import component from 'module';"
  _from_import_linefilter: Callable[[str], bool] = lambda line: line.startswith('import') and ';' in  line and 'from' in line and not any([match(i, line) is not None for i in ignore])
  _from_import_linemapping: Callable[[str], str] = lambda line: line.replace(';', '').replace('"', '').strip().replace('\n', '').split('from')[-1].strip()
  _from_import_extractor: List[str] = _extractor(_from_import_linefilter, _from_import_linemapping)
    
  # Gets only singleline flat imports such as "import './module';"
  _flat_import_linefilter: Callable[[str], bool] = lambda line: line.startswith('import') and ';' in line and 'from' not in line and not any([match(i, line) is not None for i in ignore])
  _flat_import_linemapping: Callable[[str], str] = lambda line: line.replace(';', '').replace('"', '').strip().replace('\n', '').split(' ')[-1].strip()
  _flat_import_extractor: List[str] = _extractor(_flat_import_linefilter, _flat_import_linemapping)


  from_imports = _from_import_extractor()
  flat_imports = _flat_import_extractor()
  multiline_imports = [] # TODO: get these if time, but I didn't find many so not crucial!
    
  return from_imports + flat_imports + multiline_imports

