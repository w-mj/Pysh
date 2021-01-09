import pysh.codec.register
import sys
import codecs


t = codecs.decode(open("source.py", encoding='utf-8').read(), encoding='pysh')
# print(t)
with open('result.py', 'w', encoding='utf-8') as f:
    f.write(t.decode('utf-8'))
