import re
from itertools import product
from utils import literals_from_body, parse_choice_atom, range_inside_choice, start_index_of_predicate
from program import Program, Rule

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

            if range_inside_choice(rule, start_index):
                predicate_start_index = start_index_of_predicate(rule, start_index)
                predicate_parenthesis_start_index = rule[:start_index].rindex("(") + 1
                predicate_parenthesis_end_index = end_index + rule[end_index:].index(")") + 1
                predicate = rule[predicate_start_index : predicate_parenthesis_start_index - 1]

                pre_range = rule[predicate_parenthesis_start_index :start_index]
                post_range = rule[end_index : predicate_parenthesis_end_index]

                atoms = []
                for i in range(start, end + 1):
                    atoms.append(f"{predicate}({pre_range}{i}{post_range}")

                result_string += rule[:predicate_start_index] + "; ".join(atoms) + rule[predicate_parenthesis_end_index:] + ". "
            else:
                for i in range(start, end + 1):
                    result_string += rule[:start_index] + str(i) + rule[end_index:] + ". "
        else:
            result_string += rule + ". "
    return result_string

def constants_from_choice_atom(atom):
    choice_elements, _ , guard = parse_choice_atom(atom)
    constants = [str(guard)] if guard != "" else []
    for head_atom, literals in choice_elements.items():
        if "(" in head_atom:
            constants.extend(re.findall(REGEX_CONSTANTS, head_atom))
        for literal in literals_from_body(literals):
            if "(" in literal:
                constants.extend(re.findall(REGEX_CONSTANTS, literal))
    return constants

def constants_from_atom(atom):
    atom = atom.strip()
    if atom.startswith("{"):
        return constants_from_choice_atom(atom)
    if "(" in atom:
        return re.findall(REGEX_CONSTANTS, atom)
    return []

def parse_arithmetic(grounded_rules):

    grounded_rules_parsed = Program("")
    for rule in grounded_rules.rules:
        rule_to_add = Rule(str(rule))
        valid = True
        for literal in rule.body:
            if "{" not in literal:
                if any([rel in literal for rel in ["<","<=",">",">=","="]]):
                    if eval(literal.replace(" = ", " == ")):
                        rule_to_add.remove_literal(literal)
                    else:
                        valid = False
                        continue
        if valid:
            grounded_rules_parsed.add_rule(rule_to_add)
    return grounded_rules_parsed


def ground(program_string):
    program_string = program_string.strip()

    if re.search(r"(?<!\d)\.\.", program_string) is not None or re.search(r"\.\.(?!\d)", program_string) is not None:
        raise SyntaxError("Program contains invalid range notation.")

    while ".." in program_string:
        program_string = expand_range(program_string).strip()
    try:
        Program(program_string)
    except SyntaxError as s:
        raise SyntaxError(f"Can not ground program due to syntax error: {s}") from s
    constants = []

    for rule in program_string[:-1].split(". "):
        if ":-" not in rule:
            head_atoms = rule.split("|")
            for head_atom in head_atoms:
                constants.extend(constants_from_atom(head_atom))
            continue
        head, body = rule.split(":-")
        head_atoms = head.split("|")
        for head_atom in head_atoms:
            constants.extend(constants_from_atom(head_atom))
        for literal in literals_from_body(body):
            constants.extend(constants_from_atom(literal))
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

    grounded_rules = parse_arithmetic(grounded_rules)
    return grounded_rules
