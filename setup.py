try:
    from setuptools import setup
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.core import setup
    from distutils.command.install import install as _install


def _post_install(install_lib):
    import shutil
    shutil.copy('pysh.pth', install_lib)

class install(_install):
    def run(self):
        self.path_file = 'pysh'
        _install.run(self)
        self.execute(_post_install, (self.install_lib,), msg="Running post install task")

version = "0.1"

setup(
    cmdclass={'install': install},
    name="pysh",
    version=version,
    download_url='https://github.com/w-mj/Pysh',
    packages=["pysh", "pysh.codec"],
    license='MIT',
    description="Run program like bash scripts.",
    long_description=open('README.md').read(),
    keywords='run program bash',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)