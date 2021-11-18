import argparse

from komponents import executor, generator


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # initialize exeutor
    executor_parser = subparsers.add_parser('execute')
    executor.initialize(executor_parser)

    # initialize generator
    generator_parser = subparsers.add_parser('generate')
    generator.initialize(generator_parser)

    args = parser.parse_args()
    # print(args)

    args.func(args)

if __name__ == '__main__':
    main()
