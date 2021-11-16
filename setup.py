from distutils.core import setup, findpackages

setup(
    name='py_project',
    version='1.0.0',
    description='Python WBS and Gantt tools.',
    author='Carter Mak',
    author_email='Carter.Mak@colorado.edu',
    url='https://github.com/cartermak/PyProject',
    packages=['py_project'],
    package_dir={'': 'lib'}
)
