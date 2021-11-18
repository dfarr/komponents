import yaml


typeMap = {
    'array': 'List',
    'boolean': 'Bool',
    'integer': 'Integer',
    'number': 'Float',
    'string': 'String'
}

def generate(crd, version, image, successCondition, failureCondition):
    inputs = [{
        'name': 'name',
        'type': 'String'
    }, {
        'name': 'namespace',
        'type': 'String',
        'default': '{{workflow.namespace}}'
    }, {
        'name': 'success_condition',
        'type': 'String',
        'default': successCondition
    }, {
        'name': 'failure_condition',
        'type': 'String',
        'default': failureCondition
    }, {
        'name': 'timeout',
        'type': 'Integer',
        'default': 3600
    }, {
        'name': 'annotations',
        'type': 'Dict',
        'default': '{}'
    }, {
        'name': 'labels',
        'type': 'Dict',
        'default': '{}'
    }]

    command = [
        'komponents',
        'execute',
        f'{crd["spec"]["group"]}/{version["name"]}',  # apiVersion
        crd['spec']['names']['kind'],                 # kind
        '--name',
        {'inputValue': 'name'},
        '--namespace',
        {'inputValue': 'namespace'},
        '--success-condition',
        {'inputValue': 'success_condition'},
        '--failure-condition',
        {'inputValue': 'failure_condition'},
        '--timeout',
        {'inputValue': 'timeout'},
        '--annotations',
        {'inputValue': 'annotations'},
        '--labels',
        {'inputValue': 'labels'}
    ]

    root = version['schema']['openAPIV3Schema']['properties']['spec']

    for node in traverse(root):
        name = '_'.join(node['path']).lower()
        inputs += [{
            'name': name,
            'type': typeMap[node['type']],
            'description': node['description'],
            'optional': True
        }]
        command += [
            '--param',
            '.'.join(node['path']),
            node['type'],
            {'inputValue': name}
        ]

    return {
        'name': crd['spec']['names']['singular'],
        'inputs': inputs,
        'implementation': {
            'container': {
                'image': image,
                'command': command
            }
        }
    }

def traverse(node, path=[]):
    type_ = 'string' if 'x-kubernetes-int-or-string' in node else node['type']

    if type_ == 'object':
        args = []
        if 'properties' in node:
            for name, node in node['properties'].items():
                args += traverse(node, path + [name])
        elif 'additionalProperties' in node:
            # how to handle these?
            pass

        return args

    elif type_ in typeMap:
        return [{
            'path': path,
            'type': type_,
            'description': node['description'] if 'description' in node else ''
        }]

    else:
        print('Unrecognised type:', type_)

    return []


def main(crd, image, successCondition, failureCondition):
    for version in crd['spec']['versions']:
        component = generate(
            crd,
            version,
            image,
            successCondition,
            failureCondition)

        yield version['name'], component
