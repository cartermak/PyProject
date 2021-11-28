from distutils.core import setup

setup(
    name='pyproject',
    version='1.0.0',
    description='Python WBS and Gantt tools.',
    author='Carter Mak',
    author_email='Carter.Mak@colorado.edu',
    url='https://github.com/cartermak/PyProject',
    packages=['pyproject'],
    package_dir={'': 'src'},
    install_requires=[
        'matplotlib',
        'numpy'
    ]
)
