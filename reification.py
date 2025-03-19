from program import Program, Rule
from utils import parse_choice_atom, choice_literal_of_rule, relations, relations_rev, choice_atom_without_relation


def add_reified_atom(atom, atoms, rule_index, reified, amount_of_rules):
    if atom not in atoms:
        atoms[atom] = amount_of_rules + len(atoms) + 1
    current_atom_index = atoms[atom]
    reified.add_rule(
        f"literal_tuple({current_atom_index}, {current_atom_index}).")
    reified.add_rule(f"atom_tuple({rule_index}, {current_atom_index}).")
    reified.add_rule(f"literal_tuple({rule_index}).")
    reified.add_rule(f"literal_tuple({current_atom_index}).")

def add_reified_literal(literal, atoms, rule_index, reified, amount_of_rules):
    reified.add_rule(f"literal_tuple({rule_index}).")
    negated = False
    if "not" in literal:
        literal = literal.replace("not ", "")
        negated = True
    if literal not in atoms:
        atoms[literal] = amount_of_rules + len(atoms) + 1
    current_atom_index = atoms[literal]
    reified.add_rule(f"literal_tuple({current_atom_index}).")
    reified.add_rule(
            f"literal_tuple({current_atom_index}, {current_atom_index}).")
    reified.add_rule(
        f"literal_tuple({rule_index}, {"-" if negated else ""}{current_atom_index}).")


def add_reified_weighted_literal(weighted_literal, atoms, rule_index, reified, amount_of_rules):
    reified.add_rule(f"weighted_literal_tuple({rule_index}).")
    negated = False
    if "not" in weighted_literal:
        weighted_literal = weighted_literal.replace("not ", "")
        negated = True

    if weighted_literal not in atoms:
        atoms[weighted_literal] = amount_of_rules + len(atoms) + 1

    current_atom_index = atoms[weighted_literal]
    reified.add_rule(
            f"literal_tuple({current_atom_index}, {current_atom_index}).")
    reified.add_rule(
        f"weighted_literal_tuple({rule_index}, {"-" if negated else ""}{current_atom_index}, 1).")

def manual_reify_head(head, atoms, rule_index, reified, amount_of_rules):
    if head == []:
        return
    for head_atom in head:
        add_reified_atom(head_atom, atoms, rule_index, reified, amount_of_rules)


def manual_reify_body(body, atoms, rule_index, reified, amount_of_rules):
    for body_literal in body:
        add_reified_literal(body_literal, atoms, rule_index, reified, amount_of_rules)

def manual_reify_rule(rule, atoms, rule_index, reified, amount_of_rules):
    manual_reify_body(rule.body, atoms, rule_index, reified, amount_of_rules)
    manual_reify_head(rule.head, atoms, rule_index, reified, amount_of_rules)

def manual_reify_choice_body(rule, atoms, rule_index, reified, amount_of_rules):
    choice_atom = choice_literal_of_rule(rule.body)
    choice_elements, relation, guard = parse_choice_atom(choice_atom)
    guard = int(guard)
    for choice_element_key in choice_elements:
        add_reified_weighted_literal(choice_element_key, atoms, f"l{rule_index}", reified, amount_of_rules)

    rule_without_choice_atom = rule
    rule_without_choice_atom.remove_literal(choice_atom)

    # rule for choice information
    reified.add_rule(f"rule(disjunction(f{rule_index}), normal(f{rule_index})).")
    if relation != "":
        manual_reify_rule(Rule(f"choice_info({rule_index}, {relations_rev[relation]}, {guard})."), atoms, f"f{rule_index}", reified, amount_of_rules)
    else:
        manual_reify_rule(Rule(f"choice_info({rule_index})."), atoms, f"f{rule_index}", reified, amount_of_rules)

    if relation == "":
        relation = ">="
        guard = 0

    if ">" == relation:
        rule_without_choice_atom.add_literal(f"helper(l{rule_index})")
        reified.add_rule(f"rule(disjunction(l{rule_index}), sum(l{rule_index},{guard + 1})).")
        manual_reify_rule(Rule(f"helper(l{rule_index})."), atoms, f"l{rule_index}", reified, amount_of_rules)

    if ">=" == relation:
        rule_without_choice_atom.add_literal(f"helper(l{rule_index })")
        reified.add_rule(f"rule(disjunction(l{rule_index}), sum(l{rule_index},{guard})).")
        manual_reify_rule(Rule(f"helper(l{rule_index})."), atoms, f"l{rule_index}", reified, amount_of_rules)

    if "<" == relation:
        rule_without_choice_atom.add_literal(f"not helper(l{rule_index})")
        reified.add_rule(f"rule(disjunction(l{rule_index}), sum(l{rule_index},{guard})).")
        manual_reify_rule(Rule(f"helper(l{rule_index})."), atoms, f"l{rule_index}", reified, amount_of_rules)

    if "<=" == relation:
        rule_without_choice_atom.add_literal(f"not helper(l{rule_index})")
        reified.add_rule(f"rule(disjunction(l{rule_index}), sum(l{rule_index},{guard + 1})).")
        manual_reify_rule(Rule(f"helper(l{rule_index})."), atoms, f"l{rule_index}", reified, amount_of_rules)

    if "=" == relation:
        rule_without_choice_atom.add_literal(f"helper(n{rule_index})")
        reified.add_rule(f"rule(disjunction(l{rule_index}), sum(l{rule_index},{guard})).")
        manual_reify_rule(Rule(f"helper(l{rule_index})."), atoms, f"l{rule_index}", reified, amount_of_rules)

        reified.add_rule(f"rule(disjunction(m{rule_index}), sum(m{rule_index},{guard + 1})).")
        for choice_element_key in choice_elements:
            add_reified_weighted_literal(choice_element_key, atoms, f"m{rule_index}", reified, amount_of_rules)
        manual_reify_rule(Rule(f"helper(m{rule_index})."), atoms, f"m{rule_index}", reified, amount_of_rules)

        reified.add_rule(f"rule(disjunction(n{rule_index}), normal(n{rule_index})).")
        manual_reify_rule(Rule(f"helper(n{rule_index}):- helper(l{rule_index}), not helper(m{rule_index})."), atoms, f"n{rule_index}", reified, amount_of_rules)

    manual_reify_rule(rule_without_choice_atom, atoms, rule_index, reified, amount_of_rules)

def add_reified_helper_b_rule(atoms, rule_index, reified, amount_of_rules, choice_elements, guard):
    reified.add_rule(f"rule(disjunction(b{rule_index}), sum(b{rule_index},{guard})).")
    rule_b = Rule(f"helper(b{rule_index}).")
    for choice_element_key in choice_elements.keys():
        add_reified_weighted_literal(choice_element_key, atoms, f"b{rule_index}", reified, amount_of_rules)
    manual_reify_rule(rule_b, atoms, f"b{rule_index}", reified, amount_of_rules)

def manual_reify_choice_head(rule, atoms, rule_index, reified, amount_of_rules):
    choice_elements, relation, guard = parse_choice_atom(rule.head[0])
    for atom in choice_elements:
        add_reified_atom(atom, atoms, rule_index, reified, amount_of_rules)

    add_reified_literal(f"helper(a{rule_index})", atoms, rule_index, reified, amount_of_rules)
    reified.add_rule(f"rule(disjunction(a{rule_index}), normal(a{rule_index})).")
    rule_a = Rule(f"helper(a{rule_index}).")
    rule_a.body = rule.body
    manual_reify_rule(rule_a, atoms, f"a{rule_index}", reified, amount_of_rules)

    # rule for choice information
    reified.add_rule(f"rule(disjunction(f{rule_index}), normal(f{rule_index})).")
    if relation != "":
        guard = int(guard)
        manual_reify_rule(Rule(f"choice_info({rule_index}, {relations_rev[relation]}, {guard})."), atoms, f"f{rule_index}", reified, amount_of_rules)
    else:
        guard = 0
        manual_reify_rule(Rule(f"choice_info({rule_index})."), atoms, f"f{rule_index}", reified, amount_of_rules)

    if ">" == relation:
        add_reified_helper_b_rule(atoms, rule_index, reified, amount_of_rules, choice_elements, guard +1)

        reified.add_rule(f"rule(disjunction(c{rule_index}), normal(c{rule_index})).")
        rule_c = Rule(f":- helper(a{rule_index}), not helper(b{rule_index}).")
        manual_reify_rule(rule_c, atoms, f"c{rule_index}", reified, amount_of_rules)

    if ">=" == relation:
        add_reified_helper_b_rule(atoms, rule_index, reified, amount_of_rules, choice_elements, guard)

        reified.add_rule(f"rule(disjunction(c{rule_index}), normal(c{rule_index})).")
        rule_c = Rule(f":- helper(a{rule_index}), not helper(b{rule_index}).")
        manual_reify_rule(rule_c, atoms, f"c{rule_index}", reified, amount_of_rules)

    if "<" == relation:
        add_reified_helper_b_rule(atoms, rule_index, reified, amount_of_rules, choice_elements, guard)

        reified.add_rule(f"rule(disjunction(c{rule_index}), normal(c{rule_index})).")
        rule_c = Rule(f"helper(c{rule_index}) :- not helper(b{rule_index}).")
        manual_reify_rule(rule_c, atoms, f"c{rule_index}", reified, amount_of_rules)

        reified.add_rule(f"rule(disjunction(d{rule_index}), normal(d{rule_index})).")
        rule_d = Rule(f":- helper(a{rule_index}) , not helper(c{rule_index}).")
        manual_reify_rule(rule_d, atoms, f"d{rule_index}", reified, amount_of_rules)

    if "<=" == relation:
        add_reified_helper_b_rule(atoms, rule_index, reified, amount_of_rules, choice_elements, guard + 1)

        reified.add_rule(f"rule(disjunction(c{rule_index}), normal(c{rule_index})).")
        rule_c = Rule(f"helper(c{rule_index}) :- not helper(b{rule_index}).")
        manual_reify_rule(rule_c, atoms, f"c{rule_index}", reified, amount_of_rules)

        reified.add_rule(f"rule(disjunction(d{rule_index}), normal(d{rule_index})).")
        rule_d = Rule(f":- helper(a{rule_index}), not helper(c{rule_index}).")
        manual_reify_rule(rule_d, atoms, f"d{rule_index}", reified, amount_of_rules)

    if "=" == relation:
        add_reified_helper_b_rule(atoms, rule_index, reified, amount_of_rules, choice_elements, guard)

        reified.add_rule(f"rule(disjunction(c{rule_index}), sum(c{rule_index},{guard + 1})).")
        rule_c = Rule(f"helper(c{rule_index}).")
        for choice_element_key in choice_elements:
            add_reified_weighted_literal(choice_element_key, atoms, f"c{rule_index}", reified, amount_of_rules)
        manual_reify_rule(rule_c, atoms, f"c{rule_index}", reified, amount_of_rules)

        reified.add_rule(f"rule(disjunction(d{rule_index}), normal(d{rule_index})).")
        rule_d = Rule(f"helper(d{rule_index}) :- helper(b{rule_index}), not helper(c{rule_index}).")
        manual_reify_rule(rule_d, atoms, f"d{rule_index}", reified, amount_of_rules)

        reified.add_rule(f"rule(disjunction(e{rule_index}), normal(e{rule_index})).")
        rule_e = Rule(f":- helper(a{rule_index}), not helper(d{rule_index}).")
        manual_reify_rule(rule_e, atoms, f"e{rule_index}", reified, amount_of_rules)

def manual_reify_choice(rule, atoms, rule_index, reified, amount_of_rules):
    if rule.is_choice():
        manual_reify_choice_head(rule, atoms, rule_index, reified, amount_of_rules)
    else:
        manual_reify_choice_body(rule, atoms, rule_index, reified, amount_of_rules)


def manual_reify(program, S, meta_atoms):
    atoms = {}
    reified_program = Program("")
    rules = program.rules
    amount_of_rules = len(rules)
    for rule_index, rule in enumerate(rules):
        rule_type = "choice" if rule.is_choice() else "disjunction"
        if rule in S.rules or rule in meta_atoms:
            reified_program.add_rule(
                f"rule({rule_type}({rule_index}), normal({rule_index})).")
        else:
            reified_program.add_rule(f"{{rule({rule_type}({rule_index}), normal({rule_index}))}}.")

        if rule.contains_choice():
            manual_reify_choice(rule, atoms, rule_index,
                                reified_program, amount_of_rules)
            continue

        if rule.is_constraint():
            manual_reify_body(rule.body, atoms, rule_index,
                              reified_program, amount_of_rules)
            continue
        if rule.is_fact():
            manual_reify_head(rule.head, atoms, rule_index,
                              reified_program, amount_of_rules)
            continue

        manual_reify_rule(rule, atoms, rule_index,
                          reified_program, amount_of_rules)

    for atom, atom_id in atoms.items():
        reified_program.add_rule(f"output({atom}, {atom_id}).")
    return reified_program

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
                rule_head.append(constant)
    return rule_head


def reified_body_to_original_body(body, literals_of_rules_dict, weighted_literals_of_rule_dict, outputs_dict):
    rule_body = []
    if "normal" in body:
        body = body.replace("normal(", "")[:-1]
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
    else:
        guard = body.split(",")[1][:-1]
        body = body.replace("sum(","")[:-1].split(",")[0]
        if body in weighted_literals_of_rule_dict:
            for body_id in weighted_literals_of_rule_dict[body]:
                negated = False
                if body_id.startswith("-"):
                    body_id = body_id.replace("-","")
                    negated = True
                constant = outputs_dict[body_id]
                if negated:
                    constant = "not " + constant
                rule_body.append(constant)
        rule_body = [f"{{{"; ".join(rule_body)}}} >= {guard}"]
    return rule_body

def find_choice_head_with_id(program, literal):
    for rule in program.rules:
        if rule.is_choice() and literal in rule.body:
            return rule.head[0]

def find_choice_body_with_id(program, atom):
    for rule in program.rules:
        if atom in rule.head:
            return rule.body

def find_choice_rule_with_id(program, rule_id):
    for rule in program.rules:
        if f"helper(l{rule_id})" in rule.body or f"not helper(l{rule_id})" in rule.body:
            if not f"not helper(m{rule_id})" in rule.body:
                choice_rule = Rule(str(rule))
                if f"helper(l{rule_id})" in rule.body:
                    choice_rule.remove_literal(f"helper(l{rule_id})")
                else:
                    choice_rule.remove_literal(f"not helper(l{rule_id})")
                program.remove_rule(rule)
                return choice_rule

    for rule in program.rules:
        if f"helper(n{rule_id})" in rule.body:
            choice_rule = Rule(str(rule))
            choice_rule.remove_literal(f"helper(n{rule_id})")
            program.remove_rule(rule)
            return choice_rule

def recreate_choice_rules_head(normal_program, choice_info_elements):
    for choice_rule in choice_info_elements:
        rule_id = choice_rule[0]
        choice_head = find_choice_head_with_id(normal_program, f"helper(a{rule_id})")
        if choice_head is None:
            continue
        if len(choice_rule) > 1:
            choice_body = find_choice_body_with_id(normal_program, f"helper(a{rule_id})")
            relation = choice_rule[1]
            guard = choice_rule[2]
            if choice_body != []:
                normal_program.add_rule(f"{choice_head}{relations[relation]}{guard} :- {",".join(choice_body)}.")
            else:
                normal_program.add_rule(f"{choice_head}{relations[relation]}{guard}.")
        else:
            choice_body = find_choice_body_with_id(normal_program, f"helper(a{rule_id})")
            if choice_body != []:
                 normal_program.add_rule(f"{choice_head} :- {",".join(choice_body)}.")
            else:
                normal_program.add_rule(f"{choice_head}.")

def recreate_choice_rules_body(normal_program, choice_info_elements):
    for choice_rule_info in choice_info_elements:
        rule_id = choice_rule_info[0]
        choice_rule = find_choice_rule_with_id(normal_program, rule_id)
        
        if choice_rule is None:
            continue

        choice_rule_body = find_choice_body_with_id(normal_program, f"helper(l{rule_id})")
        choice_atom = choice_literal_of_rule(choice_rule_body)
        choice_elements = choice_atom_without_relation(choice_atom)
        
        if len(choice_rule_info) > 1:
            relation = choice_rule_info[1]
            guard = choice_rule_info[2]
            choice_rule.add_literal(f"{choice_elements}{relations[relation]}{guard}")
        else:
            choice_rule.add_literal(f"{choice_elements}")
        normal_program.add_rule(choice_rule)

def recreate_choice_rules(normal_program):
    choice_info_rules = [str(rule) for rule in normal_program.rules if "choice_info" in str(rule)]
    choice_info = [choice_info_rule[choice_info_rule.index("(") + 1 : -2] for choice_info_rule in choice_info_rules]
    choice_info_elements = [ci.split(", ") for ci in choice_info]
    recreate_choice_rules_head(normal_program, choice_info_elements)
    recreate_choice_rules_body(normal_program, choice_info_elements)

def remove_helper_rules(normal_program):
    to_remove = []
    for rule in normal_program.rules:
        if "helper(" in str(rule) or "choice_info" in str(rule):
            to_remove.append(rule)

    for to_remove_rule in to_remove:
        normal_program.remove_rule(to_remove_rule)

###
# Transforms a Program in reified form into the normal form
##
def reified_to_original_rules(reified_program):
    reified_list = []
    for rule in reified_program.rules:
        reified_list.append(str(rule)[:-1])
    atoms = list(filter(lambda r: r.startswith("atom"), reified_list))
    literals = list(filter(lambda r: r.startswith("literal"), reified_list))
    weighted_literals = list(
        filter(lambda r: r.startswith("weighted"), reified_list))
    reified_rules = list(filter(lambda r: r.startswith(
        "rule") or r.startswith("{rule"), reified_list))
    outputs = list(filter(lambda r: r.startswith("output"), reified_list))

    atoms_of_rules_dict = reified_element_to_dict("atom_tuple", atoms)
    literals_of_rules_dict = reified_element_to_dict("literal_tuple", literals)
    weighted_literals_of_rule_dict = reified_element_to_dict("weighted_literal_tuple", weighted_literals)
    outputs_dict = reified_output_to_dict(outputs)
    normal_program = Program("")

    for rule in reified_rules:
        rule = rule.strip()
        if rule.startswith("{"):
            element = rule.replace("{rule(", "")[:-2]
        else:
            element = rule.replace("rule(", "")[:-1]
        head, body = element.split(", ", 1)
        
        rule_head = reified_head_to_original_head(
            head, atoms_of_rules_dict, outputs_dict)
        rule_body = reified_body_to_original_body(
            body, literals_of_rules_dict, weighted_literals_of_rule_dict, outputs_dict)
        if "choice" in rule:
            rule_head = "{" + '; '.join(rule_head) + "}"
        else:
            rule_head = ' | '.join(rule_head)

        if len(rule_body) == 0:
            normal_program.add_rule((f"{rule_head}."))
        else:
            normal_program.add_rule(
                (f"{rule_head} :- {', '.join(rule_body)}."))
    recreate_choice_rules(normal_program)
    remove_helper_rules(normal_program)
    return normal_program
