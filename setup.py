from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib

'''
    运行python setup.py check查看setup.py中的问题，添加了url、author、author_email
    执行python setup.py build
    执行python setup.py install
'''
SITE_PACKAGES_PATH = get_python_lib()
print(SITE_PACKAGES_PATH)
setup(
    name="pysh-run",
    version='1.1',
    #download_url='https://github.com/w-mj/Pysh',
    url='https://github.com/w-mj/Pysh',
    author='w-mj && lolydleo',
    author_email='wmj@alphamj.cn',
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