from typing import List, Dict, Set
from files import Path
from js_utils import extract_js_imports, extract_module
from common import flatten
import pyvis as vis
import networkx as nx
import math
import random

def main():

  # Can also just filter the path on only js afterwards but this speeds up crawl :)
  ignore_files: List[str] = [
    '.*node_modules.*',
    '.*notes.*',
    '.*public.*',
    '.*\\.tex.*',
    '.*\\.json',
    '.*\\.css',
    '.*\\.md',
  ]

  ignore_imports: List[str] = [
    ".*\\.css", # not interested in css import data for now
    ".*\\.json", # not interested in json import data for now either
    # ".*i18n.*", # these are translations and pretty much just noise, remember to mention in report | although what if we want to change? are the definitions hardcoded in a .js file?
    # thought about ignoring components.colors in here, but that's actually interesting because color seems very coupled!,
    # routing was also a candidate but 'components.LoadingAnimation' imports router so this seems interesting as well!!!,
  ]

  codefiles: List[Path] = list(Path('./src').delve(ignore=ignore_files))
  modules: Set[str] = set(map(extract_module, codefiles))
  imports: Dict[str, Set[str]] = { extract_module(f): set(extract_js_imports(f, ignore=ignore_imports)) for f in codefiles } 

  # Inverse imports to be able to create a better view of component dependency!
  exports: Dict[str, Set[str]] = { m: set() for m in modules }
  for module, module_imports in imports.items():
    for i in module_imports:
      exports[i].update(module)


  # Generate a graph solely considering file-to-file imports (no abstraction!)
  def generate_raw_import_graph():
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


  # Generate a graph showing imports across top level modules
  def generate_top_level_cross_imports_graph(): 
    get_top_level_module = lambda s: s.split('.')[0]

    # todo: abstract modules into a tree to work with abstraction hierarchy
    top_level_modules = set(list([get_top_level_module(m) for m in modules]))
    nx_graph = nx.Graph()
    nx_graph.add_nodes_from(top_level_modules)
    imports_from = { m: { _m: 0 for _m in top_level_modules } for m in top_level_modules }
    total_imports = { m: 0 for m in top_level_modules }
    total_exports = { m: 0 for m in top_level_modules }

    for module, module_imports in imports.items():
      for i in module_imports:
        from_module = get_top_level_module(module)
        to_module = get_top_level_module(i)
        if from_module == to_module: continue

        imports_from[to_module][from_module] += 1
        total_imports[from_module] += 1
        total_exports[to_module] += 1
        
    for from_module, to_modules in imports_from.items():
      for module, count in to_modules.items():
        if count == 0 or module == from_module: continue
        edgelabel = module + ' imports ' + from_module + ' ' + str(count) + ' times'
        nx_graph.add_edge(from_module, module, weight=2+math.log(count, 2), title=edgelabel)

    nt = vis.network.Network(height="1800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    nt.inherit_edge_colors(True)
    nt.from_nx(nx_graph)
    nt.toggle_physics(False)

    for node in nt.nodes:
      nodecolor = f'rgb({random.randint(123,255)},{random.randint(123,255)},{random.randint(123,255)})'
      if total_exports[node['id']] == 0: continue
      node['label'] += f' [ out {total_exports[node["id"]]} / in {total_imports[node["id"]]} ]'
      node['size'] = 20 + 10*math.log(total_exports[node['id']])
      node['font']['size'] = node['size']
      node['font']['color'] = nodecolor
      node['font']['border'] = True
      node['borderWidth'] = 10
      node['color'] = nodecolor
      node['labelHighlightBold'] = True
      node['mass'] = node['size']
      node['title'] = 'module: ' + node['id']
      node['title'] += '\n TOTAL [ out ' + str(total_exports[node['id']]) + ' / in ' + str(total_imports[node['id']]) + ' ]'
      for other_module, count in imports_from[node['id']].items():
        node['title'] += '\n ' + other_module + ' [ out ' + str(count) + ' / in ' + str(imports_from[other_module][node['id']]) + ' ] '

    nt.barnes_hut()
    nt.show('top_lvl_imports.html', notebook=False)

  generate_top_level_cross_imports_graph()


  # out: times imported in other module
  # in: times importing other module

  # todo: get zeegu running and have a better look at how it operates?
  # todo: look at truck and reflect
  # todo: consider how color coupling could be improved
  # todo: take a look at routing coupling
  # todo: take a look at component changeability/redesignability
  # todo: take a look at how easy translations would be to manage
  # todo: consider the criticality of all of the above



if __name__ == '__main__': main()
