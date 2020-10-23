import codecs, encodings
from .tokenizer import pysh_tokenize, pysh_untokenize
from io import StringIO

print("Import pysh.codec.register")


def pysh_transform(stream):
    try:
        output = pysh_untokenize(pysh_tokenize(stream.readline))
    except Exception as ex:
        raise ex
    return output.encode("utf-8")


def pysh_transform_string(text):
    stream = StringIO(text)
    return pysh_transform(stream)


def search_function(encoding):
    if encoding != 'pysh':
        return None
    # Assume utf8 encoding
    from encodings import utf_8
    utf8 = encodings.search_function('utf8')

    def pysh_decode(input, errors='strict'):
        if isinstance(input, memoryview):
            input = input.tobytes().decode("utf-8")
        return utf8.decode(pysh_transform_string(input), errors)

    class pyshIncrementalDecoder(utf_8.IncrementalDecoder):
        def decode(self, input, final=False):
            self.buffer += input
            if final:
                buff = self.buffer
                self.buffer = b''
                return super(pyshIncrementalDecoder, self).decode(
                    pysh_transform_string(buff), final=True)

    class pyshStreamReader(utf_8.StreamReader):
        def __init__(self, *args, **kwargs):
            codecs.StreamReader.__init__(self, *args, **kwargs)
            self.stream = StringIO(pysh_transform(self.stream))

    return codecs.CodecInfo(
        name='pysh',
        encode=utf8.encode,
        decode=pysh_decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=pyshIncrementalDecoder,
        streamreader=pyshStreamReader,
        streamwriter=utf8.streamwriter)

codecs.register(search_function)
