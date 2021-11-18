import re
import json
import argparse
from argparse import ArgumentTypeError

from komponents.executor import k8s, utils


def generate(apiVersion, kind, name, params, annotations, labels):
    return {
        'apiVersion': apiVersion,
        'kind': kind,
        'metadata': {
            'annotations': annotations,
            'labels': labels,
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
    if type == 'array':
        return json.loads(value)
    if type == 'boolean':
        return value == 'True'
    if type == 'integer':
        return int(value)
    if type == 'number':
        return float(value)
    if type == 'string':
        return value

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
        value = utils.get(resource, lhs)

        if value is None:
            raise ArgumentTypeError(f'Condition key "{".".join(lhs)}" does not exist')

        if op == '==' and str(value) == rhs:
            return True
        if op == '!=' and str(value) != rhs:
            return True

    return False

def main(apiVersion, kind, namespace, name, params, successCondition, failureCondition, timeout, annotations, labels):
    successConditions = parseCondition(successCondition)
    failureConditions = parseCondition(failureCondition)

    # generate
    body = generate(apiVersion, kind, name, params, annotations, labels)
    print('Creating:', json.dumps(body, indent=4))

    # create
    executor = k8s.Executor(apiVersion, kind, namespace)
    resource = executor.create(body)
    print('Created:', resource.metadata.name)

    # watch
    for event in executor.watch(resource, timeout=timeout):
        if satisfies(event['raw_object'], successConditions):
            return True, f'{kind} "{resource.metadata.name}" satisfied success condition'

        if satisfies(event['raw_object'], failureConditions):
            return False, f'{kind} "{resource.metadata.name}" satisfied failure condition'

    return False, f'{kind} "{resource.metadata.name}" did not satisfy success or failure condition within {timeout}s'
