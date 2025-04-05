import re
from itertools import product
from utils import (
    elements_from_body_or_predicate,
    parse_choice_atom,
    range_inside_choice,
    start_index_of_predicate,
    choice_elements_around_index,
    str_choice_atom_from_dict,
    relation_of_atom
)
from program import Program, Rule

REGEX_CONSTANTS = r"(?!not)(?<!#)\b[a-z0-9]\w*\b(?!\()"
REGEX_RANGE = r"(\d+)\.\.(\d+)"
REGEX_VARIABLES = r"[^a-z]([A-Z]\w*)"
REGEX_SUBSTITUTION = lambda v: rf"(?<![\w]){v}(?![\w])"


def range_expanded_atom_list(rule, start_index, end_index, start, end):
    predicate_start_index = start_index_of_predicate(rule, start_index)
    predicate_parenthesis_start_index = rule[:start_index].rindex("(") + 1
    predicate_parenthesis_end_index = end_index + rule[end_index:].index(")") + 1
    predicate = rule[predicate_start_index : predicate_parenthesis_start_index - 1]

    pre_range = rule[predicate_parenthesis_start_index:start_index]
    post_range = rule[end_index:predicate_parenthesis_end_index]

    atoms = []
    for i in range(start, end + 1):
        atoms.append(f"{predicate}({pre_range}{i}{post_range}")
    return atoms


def range_info(atom):
    limits = re.search(REGEX_RANGE, atom)
    start, end = int(limits.group(1)), int(limits.group(2))
    start_index = limits.start(1)
    end_index = limits.end(2)
    return start, end, start_index, end_index

def range_expanded_rule(rule):
    limits = re.search(REGEX_RANGE, rule)
    start, end = int(limits.group(1)), int(limits.group(2))
    start_index = limits.start(1)
    end_index = limits.end(2)

    if range_inside_choice(rule, start_index):
        start_index_of_choice = rule[:start_index].rindex("{") + 1
        end_index_of_choice = rule[start_index:].index("}") + start_index
        choice_elements_with_range = choice_elements_around_index(
            rule, start_index
        )

        choice_heads_to_remove = []
        choice_heads_to_add = []
        for choice_head, choice_body in choice_elements_with_range.items():
            if ".." in choice_head:
                choice_heads_to_remove.append(choice_head)
                start, end, start_index, end_index = range_info(choice_head)
                range_atoms = range_expanded_atom_list(
                    choice_head, start_index, end_index, start, end
                )
                for range_atom in range_atoms:
                    choice_heads_to_add.append(
                        (range_atom, choice_body)
                    )
        for choice_head_to_remove in choice_heads_to_remove:
            del choice_elements_with_range[choice_head_to_remove]
        for choice_head_to_add in choice_heads_to_add:
            choice_elements_with_range[choice_head_to_add[0]] = (
                choice_head_to_add[1]
            )
        rule = (
            rule[: start_index_of_choice - 1]
            + str_choice_atom_from_dict(choice_elements_with_range)
            + rule[end_index_of_choice + 1 :]
        )
        return rule + ". "
    else:
        result_string = ""
        for i in range(start, end + 1):
            result_string += (
                rule[:start_index] + str(i) + rule[end_index:] + ". "
            )
        return result_string

def expand_range(program_string):
    result_string = ""
    for rule in re.split(r"\.\s+", program_string[:-1]):
        if ".." in rule:
            result_string += range_expanded_rule(rule)
        else:
            result_string += rule + ". "
    return result_string

def check_arithmetic_in_literal(literal, rel):
    left, right = literal.split(rel)
    if not re.search("[a-zA-Z]", left) and not re.search("[a-zA-Z]", right):
        if "," in left:
            if rel == "==":
                return left.strip() == right.strip()
            elif rel == "!=":
                return left.strip() != right.strip()
            else:
                return False
        return eval(f"{int(eval(left))}{rel}{int(eval(right))}")
    else:
        if rel == "==":
            return left.strip() == right.strip()
        if rel == "!=":
            return left.strip() != right.strip()
        else:
            raise SyntaxError(f"Can not compare names \"{left.strip()}\" and \"{right.strip()}\" with relation \"{rel}\"")

def parse_arithmetic_guard(choice_atom):
    _, relation, guard = parse_choice_atom(choice_atom)
    return choice_atom[0 : choice_atom.index(relation) + len(relation)] + str(int(eval(guard)))

def parse_arithmetic_expression_predicate(predicate):
    predicate = predicate.strip()
    terms = predicate[predicate.index("(") + 1 : -1]
    terms_list = elements_from_body_or_predicate(terms)
    terms_list = [str(int(eval(t))) if any(operator in t for operator in ["+", "-", "*", "/"]) else t for t in terms_list]
    return predicate[:predicate.index("(") + 1] + ", ".join(terms_list) + ")"

def parse_arithmetic_expression_choice(choice_atom):
    choice_elements, relation, guard = parse_choice_atom(choice_atom)
    parsed_choice_elements = []
    for choice_element in choice_elements:
        if any(operator in choice_element for operator in ["+", "-", "*", "/"]):
            parsed_choice_elements.append(parse_arithmetic_expression_predicate(choice_element))
        else:
            parsed_choice_elements.append(choice_element)
    return f"{{{"; ".join(parsed_choice_elements)}}} {relation} {guard}"


def parse_arithmetic_expressions(grounded_program):
    grounded_program_parsed = Program("")
    for rule in grounded_program.rules:
        rule_to_add = Rule(str(rule))
        if any(operator in str(rule) for operator in ["+", "-", "*", "/"]):
            for h in rule.head:
                if any(operator in h for operator in ["+", "-", "*", "/"]):
                    rule_to_add.head.remove(h)
                    if h.startswith("{"):
                        parsed_expression = parse_arithmetic_expression_choice(h)
                    else:
                        parsed_expression = parse_arithmetic_expression_predicate(h)
                    rule_to_add.head.append(parsed_expression)

            for b in rule.body:
                if any(operator in b for operator in ["+", "-", "*", "/"]):
                    rule_to_add.remove_literal(b)
                    if b.startswith("{"):
                        parsed_expression = parse_arithmetic_expression_choice(b)
                    else:
                        parsed_expression = parse_arithmetic_expression_predicate(b)
                    rule_to_add.add_literal(parsed_expression)

        grounded_program_parsed.add_rule(rule_to_add)

    return grounded_program_parsed

def parse_arithmetic_equations(grounded_program):
    grounded_program_parsed = Program("")
    for rule in grounded_program.rules:
        rule_to_add = Rule(str(rule))
        valid = True
        for literal in rule.body:
            if "{" not in literal:
                relation = relation_of_atom(literal)
                if relation is not None:
                    valid_literal = check_arithmetic_in_literal(literal, relation)
                    if valid_literal:
                        rule_to_add.remove_literal(literal)
                    else:
                        valid = False
                        break
            else:
                relation = relation_of_atom(literal)
                if relation is not None:
                    rule_to_add.remove_literal(literal)
                    rule_to_add.add_literal(parse_arithmetic_guard(literal))
                    break

        for atom in rule.head:
            if "{" not in atom:
                relation = relation_of_atom(atom)
                if relation is not None:
                    raise SyntaxError("Comparisons in rule head outside of choice atoms are not allowed.")
            else:
                relation = relation_of_atom(atom)
                if relation is not None:
                    rule_to_add.head = [h for h in rule_to_add.head if h != atom]
                    rule_to_add.head.append(parse_arithmetic_guard(atom))
                    break
        if valid:
            grounded_program_parsed.add_rule(rule_to_add)
    return grounded_program_parsed

def parse_arithmetic(grounded_program):
    grounded_program = parse_arithmetic_equations(grounded_program)
    return parse_arithmetic_expressions(grounded_program) 

def replace_variables(program_string, constants):
    grounded_program = Program("")
    for rule in re.split(r"\.\s+", program_string[:-1]):
        rule = rule.strip()
        variables = set(re.findall(REGEX_VARIABLES, rule))
        if not variables:
            grounded_program.add_rule(f"{rule}.")
            continue
        for c in list(product(constants, repeat=len(variables))):
            grounded_rule = rule
            for i, v in enumerate(variables):
                grounded_rule = re.sub(REGEX_SUBSTITUTION(v), c[i], grounded_rule)
            grounded_program.add_rule(f"{grounded_rule}.")
    return grounded_program

def constants_from_choice_atom(atom):
    choice_elements, _, guard = parse_choice_atom(atom)
    constants = re.findall(REGEX_CONSTANTS, guard)
    for head_atom, literals in choice_elements.items():
        if "(" in head_atom:
            constants.extend(re.findall(REGEX_CONSTANTS, head_atom))
        for literal in elements_from_body_or_predicate(literals):
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

def constants_of_program(program_string):
    constants = []
    for rule in re.split(r"\.\s+", program_string[:-1]):
        if ":-" not in rule:
            head_atoms = rule.split("|")
            for head_atom in head_atoms:
                constants.extend(constants_from_atom(head_atom))
            continue
        head, body = rule.split(":-")
        head_atoms = head.split("|")
        for head_atom in head_atoms:
            constants.extend(constants_from_atom(head_atom))
        for literal in elements_from_body_or_predicate(body):
            constants.extend(constants_from_atom(literal))
    return list(set(constants))

def ground(program_string, constants=None):
    program_string = program_string.strip()

    if any(aggregate in program_string for aggregate in ["#sum", "#count", "#max", "#min"]):
        raise NotImplementedError("Aggregates are not supported.")

    if re.search(r"{[^}]*:[^}]*}", program_string) is not None:
        raise NotImplementedError("Conditionals in choice atoms are not supported.")

    if (
        re.search(r"(?<!\d)\.\.", program_string) is not None
        or re.search(r"\.\.(?!\d)", program_string) is not None
    ):
        raise SyntaxError("Program contains invalid range notation.")

    while ".." in program_string:
        program_string = expand_range(program_string).strip()
    try:
        Program(program_string)
    except SyntaxError as s:
        raise SyntaxError(f"Can not ground program due to syntax error: {s}") from s

    if constants is None:
        constants = constants_of_program(program_string)

    grounded_program = replace_variables(program_string, constants)
    return parse_arithmetic(grounded_program)
