# komponents

[![Build and Publish](https://github.com/dfarr/komponents/actions/workflows/workflow.yaml/badge.svg)](https://github.com/dfarr/komponents/actions/workflows/workflow.yaml)

Generates Kubeflow Components from Kubernetes CRD specifications.

## Installation
```
pip install komponents
```

## Usage

First, generate components. Components are specifications that Kubeflow uses to define steps of a pipeline. To generate a component, pipe a CRD specification to `komponents generate`, you must provide a success and failure condition. By default, component specification are written to the `components` directory.
```
kubectl get -o yaml crd/my-crd | komponents generate --success-condition status.state==SUCCESS --failure-condition status.state==FAILURE
```

Once you have generated your components you can plug them into a Kubeflow pipeline. Each field under `spec` of the crd becomes a parameter to the component function. Nested fields are differentiated with an underscore in the parameter name.

```python
import kfp

crd_op = kfp.components.load_component('components/my-crd-group/my-crd-v1.yaml')

@kfp.dsl.pipeline()
def pipeline():
  crd_op(foo='foo', bar='bar', baz_1='baz-1', baz_2='baz-2')
```

## Development
```
python3 -m venv venv
source venv/bin/activate
pip install .
komponents --help
```
