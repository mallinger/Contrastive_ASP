import re
from itertools import product
from utils import literals_from_body
from program import Program


def ground(program_string):
    try:
        Program(program_string)
    except SyntaxError as s:
        raise SyntaxError(f"Can not ground program due to syntax error: {s}")
    constants = []
    for rule in program_string.split(".")[:-1]:
        if ":-" not in rule:
            if "(" in rule:
                constants.extend(re.findall(
                    r'(?!not)\b[a-z0-9]\w*\b(?!\()', rule))
            continue

        head, body = rule.split(":-")
        if "(" in head:
            constants.extend(re.findall(r'(?!not)\b[a-z0-9]\w*\b(?!\()', head))
        for literal in literals_from_body(body):
            if "(" in literal:
                constants.extend(re.findall(
                    r'(?!not)\b[a-z0-9]\w*\b(?!\()', literal))
    constants = list(set(constants))

    grounded_rules = Program("")
    for rule in program_string[:-1].split(". "):
        variables = set(re.findall(r'[^a-z]([A-Z]\w*)', rule))
        if not variables:
            grounded_rules.add_rule(f"{rule}.")
            continue
        for c in list(product(constants, repeat=len(variables))):
            grounded_rule = rule
            for i, v in enumerate(variables):
                grounded_rule = re.sub(
                    rf'(?<![\w]){v}(?![\w])', c[i], grounded_rule)
            grounded_rules.add_rule(f"{grounded_rule}.")
    return grounded_rules
