"""
Implement your program here. You may use 
multiple scripts if you wish as long as 
your program runs through the execution of
this file.
"""

import pickle
import re
from converter import Converter


#function to extract non-terminsal symbols
def nonterminals(expansion):
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return RE_NONTERMINAL.findall(expansion)

regex = input()
regexConverter=Converter(regex)



### Your logic here ###

output = (regexConverter.getAlphabets(), regexConverter.getGrammar())
#print(regexConverter.getAlphabets())
#print(regexConverter.getGrammar())


with open('grammar.pkl', 'wb') as outfile:
    pickle.dump(output, outfile)
