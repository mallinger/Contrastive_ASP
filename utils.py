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


def predicates_of_program(p):
    predicates = []
    for rule in p.rules:
        predicates.extend(rule.head)
        predicates.extend(rule.body)
    predicates = list(map(lambda p: p.replace("not ", ""), predicates))
    return list(set(predicates))
