
def variable_name_from_literal(outputs_dict, literals):
    for literal in literals:
        if literal in outputs_dict:
            return outputs_dict[literal]


def reverse_dict(dictionary):
    reversed_dict = {}
    for k, v in dictionary.items():
        for e in v:
            if e in reversed_dict:
                reversed_dict[e].append(k)
            if e not in reversed_dict:
                reversed_dict[e] = [k]
    return reversed_dict


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
        if letter == "," and off == 0:
            literals.append(literal[:-1].lstrip())
            literal = ""
    literals.append(literal.lstrip())
    return literals


def arity_of_literal(literal):
    if "(" not in literal:
        return 0
    return len(literals_from_body(literal.split("(", 1)[1]))


def literals_to_define(rules):
    to_define = ["active/1", "active_P_prime/1"]
    for rule in rules:
        if not rule.is_fact():
            for literal in rule.body:
                if literal.startswith("not "):
                    literal = literal.replace("not ", "")
                arity = arity_of_literal(literal)
                if "(" in literal:
                    literal = literal.split("(")[0]
                to_define.append(literal + f"/{arity}")
    return to_define


def remove_optional_support_literals(reified):
    to_remove = []
    for rule in reified.rules:
        rule_str = str(rule)
        if (
            rule_str.startswith("optional(")
            or rule_str.startswith("body_pos")
            or rule_str.startswith("body_neg")
            or rule_str.startswith("head_elem")
        ):
            to_remove.append(rule)
    for rule in to_remove:
        reified.remove_rule(rule)
