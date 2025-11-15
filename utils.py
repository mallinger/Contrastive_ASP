"""
This modules contains utility functions used in
counterfactual_account.py, counterfactual_explanation.py, reification.py, grounder.py
"""

import re


def elements_from_body_or_predicate(body_or_predicate):
    """
    Extract literals from a body or
    terms from a predicate

    Raise a SyntaxError if parentheses are malformed
    """
    off = 0
    elements = []
    element = ""
    for letter in body_or_predicate:
        element += letter
        if letter == "(":
            off += 1
        if letter == ")":
            off -= 1
            if off < 0:
                raise SyntaxError(f'Missing opening parenthesis at literal "{element}"')
        if letter == "," and off == 0:
            elements.append(element[:-1].lstrip())
            element = ""
    if off != 0:
        raise SyntaxError("Parenthesis not closed")
    elements.append(element.lstrip())
    return elements


def verify_head_formating(head):
    """
    Verify the head formating and aise SyntaxError if the input head is malformed
    """
    for h in head:
        if not h.lstrip().startswith("{") and re.search(
            r"[a-zA-Z0-9]\s+[a-zA-Z0-9]", h
        ):
            raise SyntaxError(f'Atom contains whitespace "{h}"')
        off = 0
        for letter in h:
            if letter == "(":
                off += 1
            if letter == ")":
                off -= 1
                if off < 0:
                    raise SyntaxError(f'Missing opening parenthesis at atom "{h}"')
        if off != 0:
            raise SyntaxError(f"Parenthesis not closed at atom {h}")


def verify_comma_placement(rule):
    """
    Verify the comman placement and raise a SyntaxError if a comma is not between two letters
    """
    rule = rule.replace(" ", "")
    if rule.startswith(",") or re.search(r",(?!{|#|\()(?=[^\w-])|(?<=[^\w\)]),", rule):
        raise SyntaxError("Missplaced comma")


def arity_of_literal(literal):
    """
    Return the arity of a literal
    """
    if "(" not in literal:
        return 0
    literal = literal.split("(", 1)[1]
    count = 1
    off = 0
    for letter in literal:
        if letter == "(":
            off += 1
        if letter == ")":
            off -= 1
        if letter == "," and off == 0:
            count += 1
    return count


def literals_to_define(rules):
    """
    Return a list of all predicates plus their arities
    """
    to_define = ["active/1", "active_P_prime/1"]
    for rule in rules:
        if not rule.is_fact():
            for literal in rule.body:
                if literal.startswith("{"):
                    continue
                if literal.startswith("not "):
                    literal = literal.replace("not ", "")
                arity = arity_of_literal(literal)
                if "(" in literal:
                    literal = literal.split("(")[0]
                to_define.append(literal + f"/{arity}")
    return list(set(to_define))


def predicates_of_program(p):
    """
    Return a list of all predicates of a given program
    """
    predicates = []
    for rule in p.rules:
        predicates.extend(rule.head)
        predicates.extend(rule.body)
    predicates = list(map(lambda p: p.replace("not ", ""), predicates))
    return list(set(predicates))


def remove_meta_atoms(atoms_list):
    """
    Return a list of all atoms in {atoms_list} that are not meta atoms
    """
    meta_predicates = ["explanandum", "foil", "assumption"]
    result = []
    for atoms in atoms_list:
        result.append(
            [
                atom
                for atom in atoms
                if not any(atom.startswith(m) for m in meta_predicates)
            ]
        )
    return result


def remove_reification_atoms(atoms_list):
    """
    Return a list of all atoms in {atoms_list} that are not reification helper atoms
    """
    reification_predicates = ["choice_info", "helper"]
    result = []
    for atoms in atoms_list:
        result.append(
            [
                atom
                for atom in atoms
                if not any(atom.startswith(m) for m in reification_predicates)
            ]
        )
    return result


def extract_choice_elements(choice_elements_str):
    """ 
    Return a dictionary of a given choice atom.
    
    Parameters
    ----------
    choice_elements_str : str
        The choice atom in string form without the curly brackets.
    
    Return
    ------
        A dictionary of choice elements with heads as keys and their bodies as values.
    """
    choice_elements = choice_elements_str.split(";")
    choice_elements_dict = {}
    for choice_element in choice_elements:
        if ":" in choice_element:
            atom, body = choice_element.split(":")
            choice_elements_dict[atom.strip()] = elements_from_body_or_predicate(
                body.strip()
            )
        else:
            choice_elements_dict[choice_element.strip()] = []
    return choice_elements_dict

def choice_elements_around_index(rule, index):
    """
    Return the choice elements of the choice atom in which
    the index lies in.
    Is used to get the choice elements that contain a range
    notation.
    """
    start_index_of_choice = rule[:index].rindex("{") + 1
    end_index_of_choice = rule[index:].index("}") + index
    return extract_choice_elements(rule[start_index_of_choice:end_index_of_choice])

def relation_of_atom(atom):
    """
    Return the relation symbol in an atom if present
    """
    for rel in ["<=", ">=", "!=", "==", "<", ">", "="]:
        if rel in atom:
            return rel


def parse_choice_atom(choice_atom):
    """
    Split up a choice atom into three parts:
    The choice elements, relation symbol and the guard.
    Return the three parts.
    """
    choice_elements_str = choice_atom[
        choice_atom.index("{") + 1 : choice_atom.index("}")
    ]
    choice_elements = extract_choice_elements(choice_elements_str)
    relation_guard = choice_atom[choice_atom.index("}") + 1 :].strip()
    if relation_guard != "":
        relation = relation_of_atom(relation_guard)
        return choice_elements, relation, relation_guard.replace(relation, "").strip()
    return choice_elements, "", ""


def range_inside_choice(rule, start_index):
    """
    Check whether the given start index, representing a range notation,
    is inside a choice atom.
    """
    is_inside = False
    for letter in rule[:start_index]:
        if letter == "{":
            is_inside = True
        if letter == "}":
            is_inside = False
    return is_inside


def start_index_of_predicate(rule, start_index):
    """
    Return the start index of a predicate in a rule relative
    to the given start index.
    """
    is_predicate = False
    i = -1
    for letter in rule[start_index::-1]:
        if is_predicate and not letter.isalnum():
            break
        if letter == "(":
            is_predicate = True
        i += 1
    return start_index - i


def choice_literal_of_rule(body):
    """
    Return the choice literal of a given rule.
    """
    for literal in body:
        if literal.replace("not ", "").startswith("{"):
            return literal


def choice_atom_without_relation(choice_atom):
    """
    Return only the first part of a choice atom without the relation.
    """
    return choice_atom[0 : choice_atom.index("}") + 1]


def are_choice_atoms_equal(first, second):
    """
    Check two choice atoms for equality.
    """
    choice_elements, relation, guard = parse_choice_atom(first)
    choice_elements_other, relation_other, guard_other = parse_choice_atom(second)
    if (
        choice_elements != choice_elements_other
        or relation != relation_other
        or guard != guard_other
    ):
        return False
    return True


def unfold_choice_atom_to_ordered_string(atom):
    """
    Converts a choice atom into an ordered string to make it
    comparable for hashes.
    """
    choice_elements, relation, guard = parse_choice_atom(atom)
    result = ""
    for key in sorted(choice_elements.keys()):
        values = sorted(choice_elements[key])
        result += key + ":" + ",".join(values)

    return result + relation + str(guard)

def str_choice_atom_from_dict(choice_elements_dict):
    """
    Transforms a dictionary of choice elements back
    into a choice atom in form of a string.
    """
    result = "{"
    choice_element_strs = []
    for head, choice_body in choice_elements_dict.items():
        choice_element_str = head
        if choice_body != []:
            choice_element_str += " : " + ",".join(choice_body)
        choice_element_strs.append(choice_element_str)
    result += "; ".join(choice_element_strs)
    result += "}"
    return result

def clean_atom(atom):
    """
    Return the input atom with whitespaces normalized.
    """
    atom = atom.replace(" ", "")
    atom = re.sub(r"([,:;}])", r"\1 ", atom)
    atom = atom.strip()
    atom = atom.replace(">=", ">= ")
    atom = atom.replace("<=", "<= ")
    atom = atom.replace("!=", "!= ")
    atom = atom.replace("==", "== ")
    return re.sub(r"(?<![<>=])([<>])(?![=])", r"\1 ", atom)


def clean_literal(literal):
    """
    Return the input literal with whitespaces normalized
    """
    negated = False
    if "not " in literal:
        negated = True
        literal = literal.replace("not ", "")
    literal = clean_atom(literal)
    if negated:
        literal = "not " + literal
    return literal


def clean_head(head):
    """
    Return the input head with whitespaces normalized
    """
    cleaned_head = []
    for atom in head:
        cleaned_head.append(clean_atom(atom))
    return cleaned_head


def clean_body(body):
    """
    Return the input body with whitespaces normalized
    """
    cleaned_body = []
    for literal in body:
        cleaned_body.append(clean_literal(literal))
    return cleaned_body


relations = {"g": " > ", "geq": " >= ", "l": " < ", "leq": " <= ", "eq": " = ", "": ""}

relations_rev = {
    ">": "g",
    ">=": "geq",
    "<": "l",
    "<=": "leq",
    "=": "eq",
    "==": "eq",
    "": "",
}
