from setuptools import setup, find_packages


with open('README.md') as f:
   long_description = f.read()

setup(
   name='komponents',
   version='1.2',
   description='Generates Kubeflow Components from Kubernetes CRD specifications',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='David Farr',
   author_email='david_farr@intuit.com',
   packages=['komponents', 'komponents.executor', 'komponents.generator'],
   entry_points={
      'console_scripts': [
         'komponents=komponents.cli:main'
      ]
   },
   install_requires=[
      'cachetools==4.2.4',
      'certifi==2021.10.8',
      'charset-normalizer==2.0.7',
      'google-auth==2.3.3',
      'idna==3.3',
      'kubernetes==19.15.0',
      'oauthlib==3.1.1',
      'pyasn1==0.4.8',
      'pyasn1-modules==0.2.8',
      'python-dateutil==2.8.2',
      'PyYAML==6.0',
      'requests==2.26.0',
      'requests-oauthlib==1.3.0',
      'rsa==4.7.2',
      'six==1.16.0',
      'urllib3==1.26.7',
      'websocket-client==1.2.1'
   ]
)
