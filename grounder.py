import re
from itertools import product
from utils import (
    literals_from_body,
    parse_choice_atom,
    range_inside_choice,
    start_index_of_predicate,
    choice_elements_around_index,
    str_choice_atom_from_dict,
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


def expand_range(program_string):
    result_string = ""
    for rule in re.split(r"\.\s+", program_string[:-1]):
        if ".." in rule:
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
                result_string += rule + ". "
            else:
                for i in range(start, end + 1):
                    result_string += (
                        rule[:start_index] + str(i) + rule[end_index:] + ". "
                    )
        else:
            result_string += rule + ". "
    return result_string


def constants_from_choice_atom(atom):
    choice_elements, _, guard = parse_choice_atom(atom)
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

def check_arithmetic_in_literal(literal, rel):
    left, right = literal.split(rel)
    if not re.search("[a-zA-Z]", left) and not re.search("[a-zA-Z]", right):
        if "," in left:
            if rel == "==" and left.strip() == right.strip():
                return True
            elif rel == "!=" and left.strip() != right.strip():
                return True
            else:
                return False
        elif eval(f"{int(eval(left))}{rel}{int(eval(right))}"):
            return True
        else:
            return False
    else:
        if rel == "==":
            return left.strip() == right.strip()
        if rel == "!=":
            return left.strip() != right.strip()
    return False


def parse_arithmetic(grounded_program):
    grounded_program_parsed = Program("")
    for rule in grounded_program.rules:
        rule_to_add = Rule(str(rule))
        valid = True
        for literal in rule.body:
            if "{" not in literal:
                for rel in ["<=", ">=", "!=", "==", "<", ">"]:
                    if rel in literal:
                        valid_literal = check_arithmetic_in_literal(literal, rel)
                        if valid_literal:
                            rule_to_add.remove_literal(literal)
                        else:
                            valid = False
                            break

        for atom in rule.head:
            if "{" not in atom:
                for rel in ["<", "<=", ">", ">=", "!=", "=="]:
                    if rel in atom:
                        left, right = atom.split(rel)
                        if not re.search("[a-zA-Z]", left) and not re.search(
                            "[a-zA-Z]", right
                        ):
                            if eval(f"{int(eval(left))}{rel}{int(eval(right))}"):
                                valid = False
                            else:
                                rule_to_add.head = [h for h in rule_to_add.head if h != atom]
                            break
        if valid:
            grounded_program_parsed.add_rule(rule_to_add)
    return grounded_program_parsed


def global_variables(rule):
    rule = re.sub(r"#\w+\s*{[^}]*}", "", rule)
    rule = re.sub(r"{[^}]*}", "", rule)
    return set(re.findall(REGEX_VARIABLES, rule))


def replace_global_variables(program_string, constants):
    program_string_no_globals = ""
    for rule in re.split(r"\.\s+", program_string[:-1]):
        rule = rule.strip()
        variables = global_variables(rule)
        if not variables:
            program_string_no_globals += f"{rule}. "
            continue
        for c in list(product(constants, repeat=len(variables))):
            grounded_rule = rule
            for i, v in enumerate(variables):
                grounded_rule = re.sub(REGEX_SUBSTITUTION(v), c[i], grounded_rule)
            program_string_no_globals += f"{grounded_rule}. "
    return program_string_no_globals


def replace_local_variables(program_string, constants):
    grounded_rules = Program("")
    program_string = program_string.strip()
    for rule in re.split(r"\.\s+", program_string[:-1]):
        rule = rule.strip()
        limits = re.search(REGEX_VARIABLES, rule)
        if not limits:
            grounded_rules.add_rule(f"{rule}.")
            continue
        start_index = limits.start(1)
        start_index_of_choice = rule[:start_index].rindex("{") + 1
        end_index_of_choice = rule[start_index:].index("}") + start_index
        choice_elements_with_local_variable = choice_elements_around_index(
            rule, start_index
        )
        variable = limits.group(1)
        expanded_choice_elements = {}
        for constant in constants:
            for key, value in choice_elements_with_local_variable.items():
                expanded_choice_elements[key.replace(variable, constant)] = [
                    val.replace(variable, constant) for val in value
                ]

        grounded_rules.add_rule(
            Rule(
                rule[: start_index_of_choice - 1]
                + str_choice_atom_from_dict(expanded_choice_elements)
                + rule[end_index_of_choice + 1 :]
                + "."
            )
        )

    return grounded_rules

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
        for literal in literals_from_body(body):
            constants.extend(constants_from_atom(literal))
    return list(set(constants))



def ground(program_string, constants=None):
    program_string = program_string.strip()

    if any(aggregate in program_string for aggregate in ["#sum", "#count", "#max", "#min"]):
        raise NotImplementedError("Aggregates are not supported in this grounder.")

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
    
    if constants == None:
        constants = constants_of_program(program_string)

    program_string = replace_global_variables(program_string, constants)
    grounded_program = replace_local_variables(program_string, constants)
    return parse_arithmetic(grounded_program)
