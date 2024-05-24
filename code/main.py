
from files import Path

def main():

  # Can also just filter the path on only js afterwards but this speeds up crawl :)
  ignore = [
    '.*node_modules.*',
    '.*tex.*',
    '.*notes.*',
    '.*public.*',
  ]

  for p in Path('./src').delve(ignore=ignore):
    print(p.path)

if __name__ == '__main__': main()
