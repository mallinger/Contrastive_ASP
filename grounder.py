import re
from itertools import product
from utils import literals_from_body
from program import Program

REGEX_CONSTANTS = r"(?!not)\b[a-z0-9]\w*\b(?!\()"
REGEX_RANGE = r"(\d+)\.\.(\d+)"
REGEX_VARIABLES = r"[^a-z]([A-Z]\w*)"
REGEX_SUBSTITUTION = lambda v: rf"(?<![\w]){v}(?![\w])"

def expand_range(program_string):
    result_string = ""
    for rule in program_string[:-1].split(". "):
        if ".." in rule:
            limits = re.search(REGEX_RANGE, rule)
            start, end = int(limits.group(1)), int(limits.group(2))
            start_index = limits.start(1)
            end_index = limits.end(2)
            for i in range(start, end + 1):
                result_string += rule[:start_index] + str(i) + rule[end_index:] + ". "
        else:
            result_string += rule + ". "
    return result_string

def ground(program_string):

    while ".." in program_string:
        program_string = expand_range(program_string).strip()

    try:
        Program(program_string)
    except SyntaxError as s:
        raise SyntaxError(f"Can not ground program due to syntax error: {s}")
    constants = []

    for rule in program_string[:-1].split(". "):
        if ":-" not in rule:
            head_atoms = rule[:-1].split("|")
            for head_atom in head_atoms:
                if "(" in head_atom:
                    constants.extend(re.findall(REGEX_CONSTANTS, head_atom))
            continue
        head, body = rule.split(":-")
        head_atoms = head.split("|")
        for head_atom in head_atoms:
            if "(" in head_atom:
                constants.extend(re.findall(REGEX_CONSTANTS, head_atom))
        for literal in literals_from_body(body):
            if "(" in literal:
                constants.extend(re.findall(REGEX_CONSTANTS, literal))
    constants = list(set(constants))


    grounded_rules = Program("")
    for rule in program_string[:-1].split(". "):
        rule = rule.strip()
        variables = set(re.findall(REGEX_VARIABLES, rule))
        if not variables:
            grounded_rules.add_rule(f"{rule}.")
            continue
        for c in list(product(constants, repeat=len(variables))):
            grounded_rule = rule
            for i, v in enumerate(variables):
                grounded_rule = re.sub(REGEX_SUBSTITUTION(v), c[i], grounded_rule)
            grounded_rules.add_rule(f"{grounded_rule}.")
    return grounded_rules
