import functools
import string

REGEX_GRAMMAR = {
    "<start>": [["<regex>"]],
    "<regex>": [
        ["<concatenation_expression>", "|", "<regex>"],
        ["<concatenation_expression>"],
    ],
    "<concatenation_expression>": [
        ["<expression>", "<concatenation_expression>"],
        ["<expression>"],
    ],
    "<expression>": [
        ["<regex_star>"],
        ["<unit_expression>"],
    ],
    "<unit_expression>": [
        ["<alpha>"],
        ["<paren_expression>"],
    ],
    "<paren_expression>": [
        ["(", "<regex>", ")"],
    ],
    "<regex_star>": [
        ["<unit_expression>", "*"],
    ],
    "<alpha>": [[c] for c in string.printable if c not in "()*|"],
}

REGEX_START = "<start>"


class Parser:
    def __init__(self, grammar):
        """
        Initialise the class with a grammar. This is called by __init__ and should not be called directly
        """
        self.grammar = grammar

    @functools.lru_cache(maxsize=None)
    def unify_key(self, key, text, at=0):
        """
        Unify a key with its value. This is the entry point for parsing grammars. The return value is a
        tuple of the length of the unification and a tuple of the key and the value that should be substituted for the key.
        """
        # Return the position of the first occurrence of the key in the
        # grammar.
        if key not in self.grammar:
            # Return the position of the first element in the text.
            if text[at:].startswith(key):
                return (at + len(key), (key, []))
            else:
                return (at, None)
        rules = self.grammar[key]
        # Returns length key result for each rule in rules.
        for rule in rules:
            length, result = self.unify_rule(rule, text, at)
            # Return length key result.
            if result is not None:
                return length, (key, result)
        return (0, None)

    def unify_rule(self, parts, text, from_index):
        """
        Unify a list of parts. This is the entry point for the parser. It returns a tuple ( from_index results ) where
        from_index is the index of the first part that failed to unify and results is a list of results that were unifyd.
        """
        results = []
        # Returns the index of the first part of the key in the parts.
        for part in parts:
            from_index, result = self.unify_key(part, text, from_index)
            # Return the result of the operation.
            if result is None:
                return from_index, None
            results.append(result)
        return from_index, results


class RegexToGrammar:
    def __init__(self):
        """
        Initialise the parser and counters. This is called by __init__ and should not be called directly by user
        """
        self.parser = Parser(REGEX_GRAMMAR)
        self.counter, self.single_rules, self.star_definitions = 0, {}, {}

    def new_key(self):
        """
        Generate a new key. This is used to distinguish between keys that have been added to the cache and
        those that have not been removed.
        """
        self.counter += 1
        return "<%d>" % self.counter

    def to_grammar(self, input_expression):
        """
        Converts regular expression to grammar. This is the inverse of : meth : ` parse `. The first child is
        converted to a string and optimised for use with
        """
        length, (key, children) = self.parser.unify_key(
            REGEX_START, input_expression)
        grammar, start = self.convert_regex(children[0])
        return self.optimise(grammar, start), start

    def convert_regex(self, node):
        """
        Convert a regular expression node to a grammar. This is used to convert grammars that
        are in the grammars list of regular expressions.
        """
        key, (child, *children) = node
        grammar, key = self.convert_concatenation_expression(child)
        rules = [[key]]
        match len(children):
            case 0:
                return grammar, key  # <concatenation_expression>
            case 1:
                rules.append([])  # <concatenation_expression> |
            case 2:  # <concatenation_expression> | <regex>
                grammar2, key2 = self.convert_regex(children[1])
                # if grammar2 is not set to a grammar2 key2. extend rules if
                # not set.
                if not grammar and grammar2:  # <concatenation_expression> was <alpha>
                    grammar2[key2].extend(rules)
                    return grammar2, key2
                rules.append([key2])
                grammar = {**grammar, **grammar2}
        new_key = self.new_key()
        return {**grammar, **{new_key: rules}}, new_key

    def convert_concatenation_expression(self, node):
        """
        Convert a concatenation expression into a grammar. This is used to generate rules for
        concatenation expressions that are in the form of a list of tuples where each tuple
        is of the form ( key expression )
        <expression> <concatenation_expression> | <expression>
        """
        key, (child, *children) = node
        grammar, key = self.convert_expression(child)
        # Returns the grammar and key for the current grammar.
        if not children:
            return grammar, key
        grammar2, key2 = self.convert_concatenation_expression(children[0])
        rule = [key, key2]
        new_key = self.new_key()
        self.single_rules[new_key] = rule
        return {**grammar, **grammar2, **{new_key: [rule]}}, new_key

    def convert_expression(self, node):
        """
        Convert a node to a regular expression. This is used to convert expressions
        that start with a regex star to a regular expression
        """
        _key, (child, *children) = node
        match child[0]:
            case "<regex_star>":
                return self.convert_regex_star(child)
            case "<unit_expression>":
                return self.convert_unit_expression(child)

    def convert_regex_star(self, node):  # <unit_expression> '*'
        """
        Convert a regular expression star into a grammar. This is used to define a star
        that can be used in an expression
        """
        key, (child, *children) = node
        grammar, key = self.convert_unit_expression(child)
        # Return grammar star_definitions key. If key is not in self.
        # star_definitions return grammar. star_definitions key.
        if key in self.star_definitions:
            return grammar, self.star_definitions[key]
        new_key = self.new_key()
        self.star_definitions[key] = new_key
        return {**grammar, **{new_key: [[key, new_key], []]}}, new_key

    def convert_unit_expression(self, node):
        """
        Convert a unit expression to a Python object. This is used to convert expressions
        that start with a letter or an alphabetic character to a Python object
        """
        _key, (child, *children) = node
        match child[0]:
            case "<alpha>":
                return self.convert_alpha(child)
            case "<paren_expression>":
                return self.convert_regex_paren(child)

    def convert_alpha(self, node):
        """
        Convert a node in the alpha tree to a key value pair.
        """
        key, (child, *children) = node
        return {}, child[0]

    def convert_regex_paren(self, node):
        """
        Convert a regular expression node to a string.
        """
        key, (op, child, cl) = node
        return self.convert_regex(child)

    def optimise_key(self, grammar, nk, nrule):
        """
        Optimise a grammar by adding nrule to the end of the rule that matches the k.
        This is used to reduce the number of rules that are added to the grammar to a certain number
        replace instances of nk with nrule
        """
        new_grammar = {}
        # Add all rules in grammar to the grammar.
        for k in grammar:
            # Skip the k th element of the list.
            if k == nk:
                continue
            new_grammar[k] = []
            # Add the grammar k rules to the grammar.
            for rule in grammar[k]:
                new_rule = []
                new_grammar[k].append(new_rule)
                # Add the token to the rule.
                for token in rule:
                    # append token to rule if token nk
                    if token == nk:
                        new_rule.extend(nrule)
                    else:
                        new_rule.append(token)
        return new_grammar

    def optimise(self, grammar, start):
        """
        Optimise a grammar by applying rules that have been added to the Grammar.
        This is a copy of the grammar that is modified in-place.

        """
        grammar_copy = dict(grammar)
        # optimise the key in the single_rules.
        for k in reversed(self.single_rules):
            # Skip the start of the loop.
            if k == start:
                continue
            grammar_copy = self.optimise_key(
                grammar_copy, k, self.single_rules[k])
        return grammar_copy


input_regex = input()

grammar1, start = RegexToGrammar().to_grammar(input_regex)
grammar = {k: ["".join(r) for r in grammar1[k]] for k in grammar1}
grammar["<S>"] = [start]
output = ([], grammar)

# with open('grammar.pkl', 'wb') as outfile:
#    pickle.dump(output, outfile)

print(output)