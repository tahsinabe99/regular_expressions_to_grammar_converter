# Python Regular Expression to Grammar Converter

 Python program that converts a single regular expression input via standard input into a grammar.


## Instructions
The program accept precisely one regular expression from stdin before terminating. This input will serve as the foundation for conversion into a grammar.
The converted grammar and the language's alphabet is saved in a pickle file. The pickle file will contain an ordered set with two elements: 
A list of all symbols in the language's alphabet.
A dictionary representing the grammar in a specific syntax.

The program does not  output anything to standard output.
The program execute using the command python3 reggie.py.

Input Syntax
Standard Rules: The programme processes regular expressions that follow standard conventions, including but not limited to union (|), Kleene star (*), and concatenation.
