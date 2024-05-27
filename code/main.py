from typing import List, Dict, Set
from files import Path
from js_utils import extract_js_imports, extract_module
from common import flatten
import pyvis as vis
import networkx as nx

def main():

  # Can also just filter the path on only js afterwards but this speeds up crawl :)
  ignore_files: List[str] = [
    '.*node_modules.*',
    '.*tex.*',
    '.*notes.*',
    '.*public.*',
    '.*.json',
    '.*.css',
    '.*.md',
  ]

  ignore_imports: List[str] = [
    ".*.css", # not interested in css import data for now
    ".*.json", # not interested in json import data for now either
    ".*i18n.*", # these are translations and pretty much just noise, remember to mention in report
    # thought about ignoring components.colors in here, but that's actually interesting because color seems very coupled!,
    # routing was also a candidate but 'components.LoadingAnimation' imports router so this seems interesting as well!!!,
  ]




  codefiles: List[Path] = list(Path('./src').delve(ignore=ignore_files))
  modules: Set[str] = set(map(extract_module, codefiles))

  imports: Dict[str, Set[str]] = { m: set() for m in modules } 
  for f in codefiles:
    imports[extract_module(f)].update(extract_js_imports(f, ignore=ignore_imports))

  exports: Dict[str, Set[str]] = { m: set() for m in flatten(imports.values()) }
  for module, module_imports in imports.items():
    for i in module_imports:
      exports[i].update(module)


  graph_nodes = modules 

  nx_graph = nx.Graph()
  nx_graph.add_nodes_from(graph_nodes)


  for module, module_imports in imports.items():
    for i in module_imports:
      nx_graph.add_edge(module, i)

  nt = vis.network.Network(height="1800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
  nt.from_nx(nx_graph)
  for node in nt.nodes:
    if node['id'] not in exports: continue
    nodesize = len(exports[node['id']])
    node['size'] = nodesize

  nt.show('raw_imports.html', notebook=False)

  # todo: make direction clearer!
  # todo: make text more visible and sized based on dot size?

  # todo: abstract modules into a tree to work with abstraction hierarchy
  # todo: look at truck
  # todo: can generate UML by using semantic analysis, find libs for this!



if __name__ == '__main__': main()
