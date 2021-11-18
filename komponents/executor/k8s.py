import os
from kubernetes import client, config, dynamic


DEV = os.environ.get('DEV') == 'true'

class Executor:
    def __init__(self, apiVersion, kind, namespace):
        self.apiVersion = apiVersion
        self.kind = kind
        self.namespace = namespace

        if DEV:
            # print('using local config')
            config.load_kube_config()
        else:
            # print('using in-cluster config')
            config.load_incluster_config()

        self.client = dynamic.DynamicClient(client.ApiClient())
        self.resource = self.client.resources.get(api_version=apiVersion, kind=kind)

    def create(self, body, **kwargs):
        return self.client.create(
            self.resource,
            namespace=self.namespace,
            body=body,
            **kwargs)

    def watch(self, resource, **kwargs):
        return self.client.watch(
            self.resource,
            namespace=self.namespace,
            field_selector=f'metadata.name={resource.metadata.name}',
            resource_version=resource.metadata.resourceVersion,
            **kwargs)
