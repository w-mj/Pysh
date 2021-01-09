from lib.pack_name import PackName
from pysh.lib.exec import Exec
from lib.generate_param import Param, generate_param

d = {
    'run': Param.COMMAND,
    'it': Param.SHORTCUT,
    'rm': None,
    'privileged': None,
    'mount': (
        {
            'type': 'bind',
            'source': '/home/abc/Document',
            'target': '/Doc'
        }, {
            'type': 'bind',
            'source': '/home/abc/Document1',
            'target': '/Doc1'
        },
    ),
    'nginx:v1.0': Param.COMMAND
}

# print(Exec(f"C:\\tools\\echo \"{generate_param(d)}\"").stdout())

_pysht_19_=Exec(f"python test.py generate 10")
a=_pysht_19_
print("run a")
_pysht_21_=PackName(a)
_pysht_20_=Exec(f"python test.py consume")
_pysht_20_.set_input(_pysht_21_)
b=_pysht_20_
_pysht_23_=PackName(a)
_pysht_22_=Exec(f"python test.py consume")
_pysht_22_.set_input(_pysht_23_)
c=_pysht_22_
print(b.stdout())
print(c.stdout())
