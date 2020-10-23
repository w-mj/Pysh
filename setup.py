from setuptools import setup
from distutils.sysconfig import get_python_lib

SITE_PACKAGES_PATH = get_python_lib()
print(SITE_PACKAGES_PATH)
setup(
    name="pysh",
    version='1.0',
    download_url='https://github.com/w-mj/Pysh',
    packages=["pysh", "pysh.codec", "pysh.lib"],
    license='MIT',
    description="Run program like bash scripts.",
    long_description=open('README.md', encoding='utf-8').read(),
    keywords='run program bash',
    data_files=[(SITE_PACKAGES_PATH, ['pysh.pth'])],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
