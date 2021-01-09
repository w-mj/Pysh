#!/usr/bin/env python


import codecs, io, encodings
import sys
import traceback
import tokenize

from . import parser
from . import token
from encodings import utf_8
from .tokenizer import pysh_tokenize, pysh_untokenize


def pysh_transform(stream):
    ##output = pysh_untokenize(pysh_tokenize(stream.readline))
    ##return output.rstrip()
    try:
        tokens = tokenize.generate_tokens(stream.readline)
        tokens = token.TokenGenerator(tokens)
        parse = parser.start(tokens)
        output = pysh_untokenize(parse)
    except Exception as ex:
        raise ex
    return output

def pysh_transform_string(input):
    stream = io.StringIO(input)
    return pysh_transform(stream)

def pysh_decode(input, errors='strict'):
    return pysh_transform_string(input), len(input)

class PyshIncrementalDecoder(utf_8.IncrementalDecoder):
    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b''
            return super(PyshIncrementalDecoder, self).decode(
                pysh_transform_string(buff), final=True)
        else:
            return ''

class PyshStreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = io.StringIO(pysh_transform(self.stream))

def search_function(encoding):
    # print(encoding)
    # if encoding != 'pysh' : return None
    # Assume utf8 encoding
    utf8 = encodings.search_function('utf8')
    return codecs.CodecInfo(
        name='pysh',
        encode=utf8.encode,
        decode=pysh_decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=PyshIncrementalDecoder,
        streamreader=PyshStreamReader,
        streamwriter=utf8.streamwriter)

codecs.register(search_function)

_USAGE = """\
Wraps a python command to allow it to recognize pysh-coded files with
no source modifications.

Usage:
    python -m pysh.codec.register -m module.to.run [args...]
    python -m pysh.codec.register path/to/script.py [args...]
"""


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '-m':
        mode = 'module'
        module = sys.argv[2]
        del sys.argv[1:3]
    elif len(sys.argv) >= 2:
        mode = 'script'
        script = sys.argv[1]
        sys.argv = sys.argv[1:]
    else:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    if mode == 'module':
        import runpy
        runpy.run_module(module, run_name='__main__', alter_sys=True)
    elif mode == 'script':
        with open(script) as f:
            global __file__
            __file__ = script
            # Use globals as our "locals" dictionary so that something
            # that tries to import __main__ (e.g. the unittest module)
            # will see the right things.
            exec(f.read(), globals(), globals())