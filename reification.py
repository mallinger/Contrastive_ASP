from program import Program


def manual_reify_head(head, atoms, rule_index, reified, amount_of_rules):
    if head == []:
        return
    for head_atom in head:
        if head_atom not in atoms:
            atoms[head_atom] = amount_of_rules + len(atoms) + 1
        current_atom_index = atoms[head_atom]
        reified.add_rule(f"atom_tuple({rule_index}, {current_atom_index}).")
        reified.add_rule(
            f"literal_tuple({current_atom_index}, {current_atom_index}).")
        reified.add_rule(f"literal_tuple({rule_index}).")
        reified.add_rule(f"literal_tuple({current_atom_index}).")


def manual_reify_body(body, atoms, rule_index, reified, amount_of_rules):
    for body_literal in body:
        reified.add_rule(f"literal_tuple({rule_index}).")
        if "not" in body_literal:
            body_literal = body_literal.replace("not ", "")
            if body_literal not in atoms:
                atoms[body_literal] = amount_of_rules + len(atoms) + 1
            current_atom_index = atoms[body_literal]
            reified.add_rule(
                f"literal_tuple({rule_index}, -{current_atom_index}).")
            reified.add_rule(
                f"literal_tuple({current_atom_index}, {current_atom_index}).")
            reified.add_rule(f"literal_tuple({current_atom_index}).")
        else:
            if body_literal not in atoms:
                atoms[body_literal] = amount_of_rules + len(atoms) + 1
            current_atom_index = atoms[body_literal]
            reified.add_rule(
                f"literal_tuple({rule_index}, {current_atom_index}).")
            reified.add_rule(
                f"literal_tuple({current_atom_index}, {current_atom_index}).")
            reified.add_rule(f"literal_tuple({current_atom_index}).")


def manual_reify(program):
    atoms = {}
    reified = Program("")
    rules = program.rules
    amount_of_rules = len(rules)
    for rule_index, rule in enumerate(rules):
        reified.add_rule(
            f"rule(disjunction({rule_index}), normal({rule_index})).")
        if rule.is_constraint():
            manual_reify_body(rule.body, atoms, rule_index,
                              reified, amount_of_rules)
            continue
        if rule.is_fact():
            manual_reify_head(rule.head, atoms, rule_index,
                              reified, amount_of_rules)
            continue

        manual_reify_head(rule.head, atoms, rule_index,
                          reified, amount_of_rules)
        manual_reify_body(rule.body, atoms, rule_index,
                          reified, amount_of_rules)

    for atom, atom_id in atoms.items():
        reified.add_rule(f"output({atom}, {atom_id}).")
    return reified


def optional_fact_to_reified(fact, rule_id):
    optional_reified = Program(
        f"optional(head(h{rule_id}), body_pos(b{rule_id}), body_neg(bn{rule_id})).")
    for h in fact.head:
        optional_reified.add_rule(f"head_elem(h{rule_id}, {h}).")
    return optional_reified


def optional_rule_to_reified(rule, rule_id):
    if rule.is_fact():
        return optional_fact_to_reified(rule, rule_id)
    body_neg = list(filter(lambda b: b.startswith("not"), rule.body))
    body_pos = [b for b in rule.body if b not in body_neg]
    body_neg = list(map(lambda b: b.replace("not ", ""), body_neg))

    optional_reified = Program(
        f"optional(head(h{rule_id}), body_pos(b{rule_id}), body_neg(bn{rule_id})).")
    if not rule.is_constraint():
        for h in rule.head:
            optional_reified.add_rule(f"head_elem(h{rule_id}, {h}).")
    for b in body_pos:
        optional_reified.add_rule(f"body_pos(b{rule_id}, {b}).")
    for b in body_neg:
        optional_reified.add_rule(f"body_neg(bn{rule_id}, {b}).")
    return optional_reified


def reified_element_to_dict(name, elements):
    elements_dict = {}
    for element in elements:
        element = element.replace(f"{name}(", "")[:-1]
        if "," in element:
            ids = element.split(", ")
            if ids[0] == ids[1]:
                continue
            if ids[0] in elements_dict:
                elements_dict[ids[0]].append(ids[1])
            else:
                elements_dict[ids[0]] = [ids[1]]
    return elements_dict


def reified_output_to_dict(reified_outputs):
    outputs_dict = {}
    for reified_output in reified_outputs:
        reified_output = reified_output.replace("output(", "")[:-1]
        atom = reified_output[0: reified_output.rindex(", ")]
        atom_id = reified_output[reified_output.rindex(", ") + 2:]
        outputs_dict[atom_id] = atom
    return outputs_dict


def reified_head_to_original_head(head, atoms_of_rules_dict, outputs_dict):
    rule_head = []
    if "disjunction" in head:
        head = head.replace("disjunction(", "")[:-1]
        if head in atoms_of_rules_dict:
            for atom_id in atoms_of_rules_dict[head]:
                constant = outputs_dict[atom_id]
                rule_head.append(constant)
    if "choice" in head:
        head = head.replace("choice(", "")[:-1]
        if head in atoms_of_rules_dict:
            for atom_id in atoms_of_rules_dict[head]:
                constant = outputs_dict[atom_id]
                rule_head.append(f"{{{constant}}}")
    return rule_head


def reified_body_to_original_body(body, literals_of_rules_dict, outputs_dict):
    rule_body = []
    if body in literals_of_rules_dict:
        for body_id in literals_of_rules_dict[body]:
            negated = False
            if body_id.startswith("-"):
                body_id = body_id.replace("-", "")
                negated = True
            constant = outputs_dict[body_id]
            if negated:
                constant = "not " + constant
            rule_body.append(constant)
    return rule_body


###
# Transforms a Program in reified form into the normal form
##
def reified_to_original_rules(reified):
    reified_list = []
    for rule in reified.rules:
        reified_list.append(str(rule)[:-1])
    atoms = list(filter(lambda r: r.startswith("atom"), reified_list))
    literals = list(filter(lambda r: r.startswith("literal"), reified_list))
    reified_rules = list(filter(lambda r: r.startswith(
        "rule") or r.startswith("{rule"), reified_list))
    outputs = list(filter(lambda r: r.startswith("output"), reified_list))

    atoms_of_rules_dict = reified_element_to_dict("atom_tuple", atoms)
    literals_of_rules_dict = reified_element_to_dict("literal_tuple", literals)
    outputs_dict = reified_output_to_dict(outputs)
    normal_program = Program("")
    for rule in reified_rules:
        if rule.startswith("{"):
            element = rule.replace("{rule(", "")[:-2]
        else:
            element = rule.replace("rule(", "")[:-1]
        head, body = element.split(", ")
        body = body.replace("normal(", "")[:-1]

        rule_head = reified_head_to_original_head(
            head, atoms_of_rules_dict, outputs_dict)
        rule_body = reified_body_to_original_body(
            body, literals_of_rules_dict, outputs_dict)
        if len(rule_body) == 0:
            normal_program.add_rule((f"{' | '.join(rule_head)}."))
        else:
            normal_program.add_rule(
                (f"{' | '.join(rule_head)} :- {', '.join(rule_body)}."))
    return normal_program
