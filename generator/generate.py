import glob
import yaml


k8sTypeToKubeflowType = {
    'array': 'List',
    'boolean': 'Bool',
    'integer': 'Integer',
    'string': 'String'
}

def generate(crd, version):
    inputs = []
    command = [
        f'{crd["spec"]["group"]}/{version["name"]}',
        crd['spec']['names']['kind']
    ]

    root = version['schema']['openAPIV3Schema']['properties']['spec']

    for node in traverse(root):
        name = '_'.join(node['path']).lower()
        inputs += [{
            'name': name,
            'type': k8sTypeToKubeflowType[node['type']],
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
                'image': 'image',
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

    elif type_ in ('array', 'boolean', 'integer', 'string'):
        return [{
            'path': path,
            'type': type_,
            'description': node['description'] if 'description' in node else ''
        }]

    else:
        print('Unrecognised type:', type_)

    return []


if __name__ == '__main__':

    # Loop through all crds
    for file in glob.glob('crds/*.yaml'):
        with open(file) as f:
            crd = yaml.safe_load(f)

        # Generate component for each version
        for version in crd['spec']['versions']:
            component = generate(crd, version)

            with open(f'dist/{component["name"]}-{version["name"]}.yaml', 'w') as f:
                yaml.dump(component, f)
