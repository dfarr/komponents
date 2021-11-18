import os
import sys
import yaml

from komponents.generator import generate


def initialize(parser):
    # set args
    parser.add_argument('--success-condition', required=True)
    parser.add_argument('--failure-condition', required=True)
    parser.add_argument('--image', default='farrd/komponents:latest')
    parser.add_argument('--output-dir', default='components')

    # set function
    parser.set_defaults(func=main)

def main(args):
    # kubectl get -o yaml crd ... | komponents generate ...
    crd = yaml.safe_load(sys.stdin)

    group = crd['spec']['group']
    name = crd['spec']['names']['singular']

    print(f'Generating component for {group}:{name}')

    directory = os.path.join(args.output_dir, group, name)
    os.makedirs(directory, exist_ok=True)

    for version, component in generate.main(crd, args.image, args.success_condition, args.failure_condition):
        with open(os.path.join(directory, f'{name}-{version}.yaml'), 'w') as f:
            yaml.dump(component, f)

    print(f'Saved component(s) to {directory}')
