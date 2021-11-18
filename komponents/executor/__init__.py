import json

from komponents.executor import execute


def initialize(parser):
    # set args
    parser.add_argument('api_version')
    parser.add_argument('kind')
    parser.add_argument('--name', required=True)
    parser.add_argument('--namespace', required=True)
    parser.add_argument('--success-condition', required=True)
    parser.add_argument('--failure-condition', required=True)
    parser.add_argument('--timeout', type=int, default=3600)
    parser.add_argument('--annotations', type=json.loads, default='{}')
    parser.add_argument('--labels', type=json.loads, default='{}')
    parser.add_argument('--param', action='append', nargs='*')

    # set function
    parser.set_defaults(func=main)

def main(args):
    success, message = execute.main(
        args.api_version,
        args.kind,
        args.namespace,
        args.name,
        [(k, t, v[0]) for k, t, *v in args.param if v],
        args.success_condition,
        args.failure_condition,
        args.timeout,
        args.annotations,
        args.labels)

    if not success:
        raise Exception(message)

    print(message)
