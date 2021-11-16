import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('apiVersion')
parser.add_argument('kind')
parser.add_argument('--param', action='append', nargs='+')

def set(spec, path, value):
    x, *xs = path

    if not xs:
        spec[x] = value
    else:
        if x not in spec:
            spec[x] = {}
        set(spec[x], xs, value)

    return spec

def generate(apiVersion, kind, params):
    return {
        'apiVersion': apiVersion,
        'kind': kind,
        'metadata': {},
        'spec': generateSpec(params)
    }

def generateSpec(params):
    spec = {}

    for path, type_, *value_ in params:
        if value_:
            if type_ == 'string':
                value = value_[0]
            elif type_ == 'integer':
                value = int(value_[0])
            elif type_ == 'boolean':
                value = value_[0] == 'True'
            elif type_ == 'array':
                value = json.loads(value_[0])
            else:
                pass

            spec = set(spec, path.split('.'), value)

    return spec

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    manifest = generate(args.apiVersion, args.kind, args.param)
    print(manifest)
