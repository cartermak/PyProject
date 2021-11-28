import argparse

def parse_args(args):

    parser = argparse.ArgumentParser()
    
    return parser.parse_args(args)


def main(args=None):
    parse_args(args)

if __name__ == '__main__':
    main()
