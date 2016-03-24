from sys import argv
from uchicagoldr.premiscreator import PremisCreator

def main():
    path = argv[1]
    pc = PremisCreator(path)
    pc.build_records()
    pc.write_records()


if __name__ == '__main__':
    main()
