import re

def literals_from_body(body):
    off = 0
    literals = []
    literal = ""
    for letter in body:
        literal += letter
        if letter == "(":
            off += 1
        if letter == ")":
            off -= 1
            if off < 0:
                raise SyntaxError(
                    f"Missing opening parenthesis at literal \"{literal}\"")
        if letter == "," and off == 0:
            literals.append(literal[:-1].lstrip())
            literal = ""
    if off != 0:
        raise SyntaxError("Parenthesis not closed")
    literals.append(literal.lstrip())
    return literals


def verify_head_formating(head):
    for h in head:
        if not h.lstrip().startswith("{") and re.search(r'[a-zA-Z0-9]\s+[a-zA-Z0-9]', h):
            raise SyntaxError(f"Atom contains whitespace \"{h}\"")
        off = 0
        for letter in h:
            if letter == "(":
                off += 1
            if letter == ")":
                off -= 1
                if off < 0:
                    raise SyntaxError(
                        f"Missing opening parenthesis at atom \"{h}\"")
        if off != 0:
            raise SyntaxError(f"Parenthesis not closed at atom {h}")

def verify_comma_placement(rule):
    rule = rule.replace(" ","")
    if rule.startswith(",") or re.search(r',(?!{|#|\()(?=[^\w-])|(?<=[^\w\)]),', rule):
        raise SyntaxError("Missplaced comma")

def arity_of_literal(literal):
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
    return to_define


def predicates_of_program(p):
    predicates = []
    for rule in p.rules:
        predicates.extend(rule.head)
        predicates.extend(rule.body)
    predicates = list(map(lambda p: p.replace("not ", ""), predicates))
    return list(set(predicates))

def remove_meta_atoms(atoms_list):
    meta_predicates = ["explanandum", "foil", "assumption"]
    result = []
    for atoms in atoms_list:
        result.append([atom for atom in atoms if not any (atom.startswith(m) for m in meta_predicates)])
    return result

def extract_choice_elements(choice_elements_str):
    choice_elements = choice_elements_str.split(";")
    choice_elements_dict = {}
    for choice_element in choice_elements:
        if ":" in choice_element:
            atom, body = choice_element.split(":")
            choice_elements_dict[atom.strip()] = literals_from_body(body.strip())
        else:
            choice_elements_dict[choice_element.strip()] = []
    return choice_elements_dict

def parse_choice_atom(choice_atom):
    choice_elements_str = choice_atom[choice_atom.index("{") + 1: choice_atom.index("}")]
    choice_elements = extract_choice_elements(choice_elements_str)
    relation_guard = choice_atom[choice_atom.index("}") + 1 :].strip()
    if relation_guard != "":
        relation, guard,_ = re.split(r'(\d+)', relation_guard)
        return choice_elements, relation.strip(), int(guard)
    return choice_elements, "", ""

def range_inside_choice(rule, start_index):
    is_inside = False
    for letter in rule[:start_index]:
        if letter == "{":
            is_inside = True
        if letter == "}":
            is_inside = False
    return is_inside

def start_index_of_predicate(rule, start_index):
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
    for literal in body:
        if literal.replace("not ", "").startswith("{"):
            return literal

def choice_atom_without_relation(choice_atom):
    return choice_atom[0:choice_atom.index("}") + 1]

def are_choice_atoms_equal(first, second):
    choice_elements, relation, guard = parse_choice_atom(first)
    choice_elements_other, relation_other, guard_other = parse_choice_atom(second)
    if choice_elements != choice_elements_other or relation != relation_other or guard != guard_other:
        return False
    return True

def unfold_choice_atom_to_ordered_string(atom):
    choice_elements, relation, guard = parse_choice_atom(atom)
    result = ""
    for key in sorted(choice_elements.keys()):
        values = sorted(choice_elements[key])
        result += key + ":" + ",".join(values)

    return result + relation + str(guard)

relations = {
    "g" : " > ",
    "geq" : " >= ",
    "l" : " < ",
    "leq" : " <= ",
    "eq" : " = ",
    "" : ""
}

relations_rev = {
    ">" : "g",
    ">=" : "geq",
    "<" : "l",
    "<=" : "leq",
    "=" : "eq",
    "" : ""
}
