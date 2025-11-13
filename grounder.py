"""
Grounder Module

This module contains the grounder, which generates a variable free answer set program
out of a given input program. 

The grounder expands range notations, parses and simplifies arithmetic expressions and equations. 

This version does not support aggregates, conditionals inside choice atoms or 
range notation with variables.
"""


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

REGEX_CONSTANTS = r"(?!not)\b[a-z0-9]\w*\b(?!\()"
REGEX_RANGE = r"(\d+)\.\.(\d+)"
REGEX_VARIABLES = r"[^a-z]([A-Z]\w*)"
REGEX_SUBSTITUTION = lambda v: rf"(?<![\w]){v}(?![\w])"


def range_expanded_atom_list(choice_head, start_index, end_index, start, end):
    """
    Return a list of atoms, each representing a step of the given range 

    Parameters
    ----------
    choice_head : str
        The choice_head containing the predicate with a range.
    start_index : int
        The starting index of the range in the rule string.
    end_index : int
        The ending index of the range in the rule string.
    start : int
        The starting integer of the range.
    end : int
        The ending integer of the range.

    Returns
    -------
    list
        A list of atoms, each representing a step of the range.
    """

    predicate_start_index = start_index_of_predicate(choice_head, start_index)
    predicate_parenthesis_start_index = choice_head[:start_index].rindex("(") + 1
    predicate_parenthesis_end_index = end_index + choice_head[end_index:].index(")") + 1
    predicate = choice_head[predicate_start_index : predicate_parenthesis_start_index - 1]

    pre_range = choice_head[predicate_parenthesis_start_index:start_index]
    post_range = choice_head[end_index:predicate_parenthesis_end_index]

    atoms = []
    for i in range(start, end + 1):
        atoms.append(f"{predicate}({pre_range}{i}{post_range}")
    return atoms


def range_info(atom):
    """
    Extract range information from a choice rule's head containing a range notation.

    Parameters
    ----------
    atom : str
        A choice rule's head that contains a range notation.

    Returns
    -------
    tuple
        A tuple (start, end, start_index, end_index) where `start` and `end` are 
        the limits of the range, and `start_index` and `end_index` are 
        the positions of the range numbers in the string.
    """

    limits = re.search(REGEX_RANGE, atom)
    start, end = int(limits.group(1)), int(limits.group(2))
    start_index = limits.start(1)
    end_index = limits.end(2)
    return start, end, start_index, end_index

def range_expanded_rule(rule):
    """
    Expand a range notation of a rule.
    In order to remove several range notations of the rule
    the function has to be called repeatedly.
    
    Parameters
    ----------
    rule : str
        A rule that contains at least one range notation.
        The '.' at the end of the rule must be removed

    Returns
    -------
    str
        The rule with one range expanded.
    """


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
    """
    Expand one range notation per rule in an answer set program.
    In order to remove all range notations the function has
    to be called repeatedly.
    
    Parameters
    ----------
    program_string : str
        The answer set program that may contain range notations as a string.

    Returns
    -------
    str
        The program string with one range notation per rule expanded.
    """
    result_string = ""
    for rule in re.split(r"\.\s+", program_string[:-1]):
        if ".." in rule:
            result_string += range_expanded_rule(rule)
        else:
            result_string += rule + ". "
    return result_string


def parse_arithmetic_expression_predicate(predicate):
    """
    Parse and evaluate arithmetic expressions within a predicate.
    
    Parameters
    ----------
    predicate : str
        A predicate string containing arithmetic expressions.

    Returns
    -------
    str
        The predicate with arithmetic expressions parsed and simplified.    
    """
    predicate = predicate.strip()
    terms = predicate[predicate.index("(") + 1 : -1]
    terms_list = elements_from_body_or_predicate(terms)
    terms_list = [str(int(eval(t))) if any(operator in t for operator in ["+", "-", "*", "/"]) else t for t in terms_list]
    return predicate[:predicate.index("(") + 1] + ", ".join(terms_list) + ")"

def parse_arithmetic_expression_choice(choice_atom):
    """
    Parse arithmetic expressions within a choice atom.
    
    Parameters
    ----------
    choice_atom : str
        A choice atom containing arithmetic expressions.

    Returns
    -------
    str
        The choice atom with arithmetic expressions parsed and simplified.
    """
    choice_elements, relation, guard = parse_choice_atom(choice_atom)
    parsed_choice_elements = []
    for choice_element in choice_elements:
        if any(operator in choice_element for operator in ["+", "-", "*", "/"]):
            parsed_choice_elements.append(parse_arithmetic_expression_predicate(choice_element))
        else:
            parsed_choice_elements.append(choice_element)
    return f"{{{"; ".join(parsed_choice_elements)}}} {relation} {guard}"


def parse_arithmetic_expressions(grounded_program):
    """
    Parse and simplify arithmetic expressions in a grounded program.

    Parameters
    ----------
    grounded_program : Program
        The grounded answer set program as a Program object.

    Returns
    -------
    Program
        A new Program object with all arithmetic expressions parsed and simplified. 
    """
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

def compare_tuples_or_names(left, right, rel):
    """
    Compare two strings or tuples using the specified equality relation.

    Parameters
    ----------
    left : str
        The left-hand string or tuple to compare.
    right : str
        The right-hand string or tuple to compare.
    rel : str
        The comparison operator, either '==' or '!='.

    Returns
    -------
    bool
        True if the comparison holds according to the specified relation, False otherwise.

    Raises
    ------
    SyntaxError
        If a relation other than '==' or '!=' is provided.
    """
    if rel == "==":
        return left.strip() == right.strip()
    if rel == "!=":
        return left.strip() != right.strip()
    raise SyntaxError(f"Can not compare tuples or names \"{left.strip()}\" and \"{right.strip()}\" with relation \"{rel}\"")

def check_arithmetic_in_literal(literal, rel):
    """
    Parse and evaluate arithmetic equation in form of a literal.
    In case of non numeric values the names or tuples are compared.
    
    Parameters
    ----------
    literal : str
        A literal containing an arithmetic equation.
    rel : str
        The relation symbol in the literal.

    Returns
    -------
    bool
        True if the comparison holds according to the specified relation, False otherwise.
    """

    left, right = literal.split(rel)
    if not re.search("[a-zA-Z]", left) and not re.search("[a-zA-Z]", right):
        if "," in left:
            return compare_tuples_or_names(left, right, rel)
        return eval(f"{int(eval(left))}{rel}{int(eval(right))}")
    else:
        return compare_tuples_or_names(left, right, rel)

def parse_arithmetic_guard(choice_atom):
    """
    Parse and evaluate arithmetic expression in a choice atom's guard if present
    
    Parameters
    ----------
    choice atom : str
        A choice atom as a string.

    Returns
    -------
    str
        The choice atom with arithmetic guard simplified.
    """

    _, relation, guard = parse_choice_atom(choice_atom)
    return choice_atom[0 : choice_atom.index(relation) + len(relation)] + str(int(eval(guard)))


def parse_arithmetic_equations(grounded_program):
    """
    Parse and evaluate arithmetic equations in a given grounded answer set program.
    In case of a choice atom the arithmetic expression in the guard is simplified if present.
    
    Parameters
    ----------
    grounded_program : Program object
        The grounded answer set program as a Program object.

    Returns
    -------
    Program
        A new Program object with arithmetic equations simplified.
    """
    grounded_program_parsed = Program("")
    for rule in grounded_program.rules:
        rule_to_add = Rule(str(rule))
        valid = True
        for literal in rule.body:
            relation = relation_of_atom(literal)
            if relation is not None:
                if "{" not in literal:
                    valid_literal = check_arithmetic_in_literal(literal, relation)
                    if valid_literal:
                        rule_to_add.remove_literal(literal)
                    else:
                        valid = False
                        break
                else:
                    rule_to_add.remove_literal(literal)
                    rule_to_add.add_literal(parse_arithmetic_guard(literal))
                    break

        for atom in rule.head:
            relation = relation_of_atom(atom)
            if relation is not None:
                if "{" not in atom:
                    raise SyntaxError("Comparisons in rule head outside of choice atoms are not allowed.")
                rule_to_add.head = [h for h in rule_to_add.head if h != atom]
                rule_to_add.head.append(parse_arithmetic_guard(atom))

        if valid:
            grounded_program_parsed.add_rule(rule_to_add)
    return grounded_program_parsed

def parse_arithmetic(grounded_program):
    """
    Parse and evaluate arithmetic equations and expressions in a given grounded answer set program.
    
    Parameters
    ----------
    grounded_program : Program object
        The grounded answer set program as a Program object.

    Returns
    -------
    str
        A ground Program object with all arithmetic parts simplified.
    """
    grounded_program = parse_arithmetic_equations(grounded_program)
    return parse_arithmetic_expressions(grounded_program)

def replace_variables(program_string, constants):
    """
    Replace all variables in an answer set program with all possible combinations of constants.
    
    ----------
    program_string : str
        The answer set program as a string containing variables.
    constants : list
        A list of constants used to replace variables.

    Returns
    -------
    Program
        A ground Program object without variables.
    """
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

def constants_from_choice_atom(choice_atom):
    """
    Extract all constant of a given choice atom.
    
    Parameters
    ----------
    atom : str
        The choice atom as a string.

    Returns
    -------
    list
        A list of constants found in the choice atom
    """

    choice_elements, _, guard = parse_choice_atom(choice_atom)
    constants = re.findall(REGEX_CONSTANTS, guard)
    for head_atom in choice_elements.keys():
        if "(" in head_atom:
            constants.extend(re.findall(REGEX_CONSTANTS, head_atom))
    return constants

def constants_from_atom(atom):
    """
    Extract all constant of a given atom.
    
    Parameters
    ----------
    atom : str
        The atom as a sting.

    Returns
    -------
    list
        A list of constants found in the atom
    """
    atom = atom.strip()
    if atom.startswith("{"):
        return constants_from_choice_atom(atom)
    if "(" in atom:
        return re.findall(REGEX_CONSTANTS, atom)
    return []

def constants_of_program(program_string):
    """
    Extract all constant of a given answer set program.
    
    Parameters
    ----------
    program_string : str
        The answer set program as a string.

    Returns
    -------
    list
        A list of constants in the program.
    """

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
    """
    Ground an answer set program by expanding ranges and parsing arithmetic expressions
    
    Parameters
    ----------
    program_string : str
        The answer set program as a string.
    constants : list, optional
        A list of the constants in the program. If it is not provided, the list is generated
         
    Returns
    -------
    str
        The grounded program as a string.
        
    Raises
    ------
    NotImplementedError
        If the program uses aggregates, conditials in choice atoms or range notation with variables.
    SyntaxError
        If the program contains invalid syntax.
    """
    program_string = program_string.strip()

    if any(aggregate in program_string for aggregate in ["#sum", "#count", "#max", "#min"]):
        raise NotImplementedError("Aggregates are not supported.")

    if re.search(r"{[^}]*:[^}]*}", program_string) is not None:
        raise NotImplementedError("Conditionals in choice atoms are not supported.")

    if (
        re.search(r"(?<!\d)\.\.", program_string) is not None
        or re.search(r"\.\.(?!\d)", program_string) is not None
    ):
        raise NotImplementedError("Range notation is not supported for variables.")

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
