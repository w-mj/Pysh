from enum import Enum


class Param(Enum):
    SHORTCUT = 1
    COMMAND = 2
    ARGUMENT = 3


def generate_list(p, prefix, delimiter):
    return delimiter.join([prefix + x for x in p])


def generate_dict(d: dict, prefix, delimiter, shortcut_prefix, assignment):
    ans = []
    for k, v in d.items():
        p = None
        if isinstance(v, Param):
            if v == Param.SHORTCUT:
                p = shortcut_prefix
            elif v == Param.COMMAND:
                p = ''
        if p is None:
            p = shortcut_prefix if len(k) == 1 else prefix

        def generate_value(value):
            if value is None or isinstance(value, Param):
                return f"{p}{k}"
            elif isinstance(value, str):
                return f"{p}{k}{assignment}{value}"
            elif isinstance(value, list):
                return f"{p}{k}{assignment}{generate_list(value, '', ',')}"
            elif isinstance(value, dict):
                return f"{p}{k}{assignment}{generate_dict(value, '', ',', '', '=')}"

        if isinstance(v, tuple):
            ans += [generate_value(x) for x in v]
        else:
            ans.append(generate_value(v))
    return delimiter.join(ans)


def generate_param(p, prefix=None, delimiter=None, shortcut=None):
    if isinstance(p, str):
        prefix = '-' if not prefix else prefix
        delimiter = ' ' if not delimiter else delimiter
        return generate_list(p, prefix, delimiter)
    if isinstance(p, dict):
        prefix = '--' if not prefix else prefix
        delimiter = ' ' if not delimiter else delimiter
        shortcut = '-' if not shortcut else shortcut
        return generate_dict(p, prefix, delimiter, shortcut, ' ')
    return str(p)

def generateParam(*args, **kwargs):
    return generate_param(*args, **kwargs)


if __name__ == '__main__':
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

    print(generate_param(d, prefix='--', shortcut='-'))
