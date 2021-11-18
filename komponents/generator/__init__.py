import os
import yaml

from komponents.generator import generate


def initialize(parser):
    # set args
    parser.add_argument('--crds', default='crds.yaml')
    parser.add_argument('--image', default='dfarr/komponents:latest')
    parser.add_argument('--output-dir', default='dist')

    # set function
    parser.set_defaults(func=main)

def main(args):
    print(f'Reading crd info from {args.crds}')

    with open(args.crds) as f:
        crds = yaml.safe_load(f)

    os.makedirs(args.output_dir, exist_ok=True)

    for filename, component in generate.main(crds, args.image):
        with open(f'{args.output_dir}/{filename}', 'w') as f:
            yaml.dump(component, f)

    print(f'Generated components to {args.output_dir}')
