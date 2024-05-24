
from files import Path

def main():
  for p in Path('~').delve():
    print(p.path)

if __name__ == '__main__': main()
