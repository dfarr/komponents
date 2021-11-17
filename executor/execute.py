import re
import json
import argparse
from argparse import ArgumentTypeError

import utils
from executor import Executor


parser = argparse.ArgumentParser()
parser.add_argument('api_version')
parser.add_argument('kind')
parser.add_argument('--name', required=True)
parser.add_argument('--namespace', required=True)
parser.add_argument('--success-condition', required=True)
parser.add_argument('--failure-condition', required=True)
parser.add_argument('--timeout', type=int, default=3600)
parser.add_argument('--param', action='append', nargs='*')

def generate(apiVersion, kind, name, params):
    return {
        'apiVersion': apiVersion,
        'kind': kind,
        'metadata': {
            'generateName': f'{name}-'
        },
        'spec': generateSpec(params)
    }

def generateSpec(params):
    spec = {}
    for key, type, value in params:
        utils.set(spec, key.split('.'), parseValue(type, value))

    return spec

def parseValue(type, value):
    if type == 'string':
        return value
    if type == 'integer':
        return int(value)
    if type == 'boolean':
        return value == 'True'
    if type == 'array':
        return json.loads(value)

    raise ArgumentTypeError(f'Unknown type "{type}". Valid types are {{array, boolean, integer, string}}')

def parseCondition(condition):
    conditions = []
    for condition in condition.strip().split(','):
        m = re.match(r'(.*)(==|!=)(.*)', condition)

        if not m:
            raise ArgumentTypeError(f'Invalid condition "{condition}"')

        conditions.append((m.group(1).split('.'), m.group(2), m.group(3)))

    return conditions

def satisfies(resource, conditions):
    for lhs, op, rhs in conditions:
        if op == '==' and str(utils.get(resource, lhs)) == rhs:
            return True
        if op == '!=' and str(utils.get(resource, lhs)) != rhs:
            return True

    return False

def run(apiVersion, kind, namespace, name, params, successConditions, failureConditions, timeout):
    # generate
    body = generate(apiVersion, kind, name, params)

    # create
    executor = Executor(apiVersion, kind, args.namespace)
    resource = executor.create(body)
    # print(resource)

    # watch
    for event in executor.watch(resource, timeout=timeout):
        if satisfies(event['raw_object'], successConditions):
            return True, f'{kind} "{resource.metadata.name}" satisfied success condition'

        if satisfies(event['raw_object'], failureConditions):
            return False, f'{kind} "{resource.metadata.name}" satisfied failure condition'

    return False, f'{kind} "{resource.metadata.name}" did complete within {timeout}s'

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    success, message = run(
        args.api_version,
        args.kind,
        args.namespace,
        args.name,
        [(k, t, v[0]) for k, t, *v in args.param if v],
        parseCondition(args.success_condition),
        parseCondition(args.failure_condition),
        args.timeout)

    if not success:
        raise Exception(message)

    print(message)
