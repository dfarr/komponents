import glob
import yaml


k8sTypeToKubeflowType = {
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

    for path, type_ in traverse(root):
        inputs += [{
            'name': '_'.join(path).lower(),
            'type': k8sTypeToKubeflowType[type_],
            'optional': True
        }]
        command += [
            '--' + '-'.join(path),
            {'inputValue': '_'.join(path).lower()}
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

        return args

    elif type_ == 'array':
        pass

    elif type_ in ('boolean', 'integer', 'string'):
        return [(path, type_)]

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
