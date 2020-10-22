import pysh.codec.register
import codecs
print(codecs.decode(open("source.py", encoding='utf-8').read(), encoding='pysh'))
