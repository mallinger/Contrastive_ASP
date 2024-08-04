from program import Program
from utils import *


def manual_reify_head(head, atoms, rule_index, reified, amount_of_rules):
    if head == []:
        return
    for head_atom in head:
        if head_atom not in atoms:
            atoms[head_atom] = amount_of_rules + len(atoms) + 1
        current_atom_index = atoms[head_atom]
        reified.add_rule(f"atom_tuple({rule_index}, {current_atom_index}).")
        reified.add_rule(f"atom_tuple({rule_index}).")
        reified.add_rule(
            f"literal_tuple({current_atom_index}, {current_atom_index}).")
        reified.add_rule(f"literal_tuple({rule_index}).")
        reified.add_rule(f"literal_tuple({current_atom_index}).")

def manual_reify(program):
    atoms = {}
    reified = Program("")
    rules = program.rules
    for rule_index, rule in enumerate(rules):
        reified.add_rule(
            f"rule(disjunction({rule_index}), normal({rule_index})).")
        manual_reify_head(rule.head, atoms, rule_index, reified, len(rules))
        if rule.is_fact():
            continue
        for body_literal in rule.body:
            if "not" in body_literal:
                body_literal = body_literal.replace("not ", "")
                if body_literal not in atoms:
                    atoms[body_literal] = len(rules) + len(atoms) + 1
                current_atom_index = atoms[body_literal]
                reified.add_rule(
                    f"literal_tuple({rule_index}, -{current_atom_index}).")
                reified.add_rule(f"literal_tuple({rule_index}).")
                reified.add_rule(
                    f"literal_tuple({current_atom_index}, {current_atom_index}).")
                reified.add_rule(f"literal_tuple({current_atom_index}).")
            else:
                if body_literal not in atoms:
                    atoms[body_literal] = len(rules) + len(atoms) + 1
                current_atom_index = atoms[body_literal]
                reified.add_rule(
                    f"literal_tuple({rule_index}, {current_atom_index}).")
                reified.add_rule(f"literal_tuple({rule_index}).")
                reified.add_rule(
                    f"literal_tuple({current_atom_index}, {current_atom_index}).")
                reified.add_rule(f"literal_tuple({current_atom_index}).")
    for atom, atom_id in atoms.items():
        reified.add_rule(f"output({atom}, {atom_id}).")
    return reified


def optional_fact_to_reified(fact, id):
    optional_reified = Program(
        f"optional(head(h{id}), body_pos(b{id}), body_neg(bn{id})).")
    for h in fact.head:
        optional_reified.add_rule(f"head_elem(h{id}, {h}).")
    return optional_reified


def optional_rule_to_reified(rule, id):
    if rule.is_fact():
        return optional_fact_to_reified(rule, id)
    body_neg = list(filter(lambda b: b.startswith("not"), rule.body))
    body_pos = [b for b in rule.body if b not in body_neg]
    body_neg = list(map(lambda b: b.replace("not ", ""), body_neg))

    optional_reified = Program(
        f"optional(head(h{id}), body_pos(b{id}), body_neg(bn{id})).")
    if not rule.is_constraint():
        for h in rule.head:
            optional_reified.add_rule(f"head_elem(h{id}, {h}).")
    for b in body_pos:
        optional_reified.add_rule(f"body_pos(b{id}, {b}).")
    for b in body_neg:
        optional_reified.add_rule(f"body_neg(bn{id}, {b}).")
    return optional_reified


def reified_element_to_dict(name, elements):
    elements_dict = {}
    for element in elements:
        element = element.replace(f"{name}(", "")[:-1]
        if "," in element:
            ids = element.split(", ")
            if ids[0] in elements_dict:
                elements_dict[ids[0]].append(ids[1])
            else:
                elements_dict[ids[0]] = [ids[1]]
    return elements_dict


def reified_output_to_dict(elements):
    elements_dict = {}
    for element in elements:
        element = element.replace("output(", "")[:-1]
        elements_dict[element[element.rindex(
            ", ") + 2:]] = element[0: element.rindex(", ")]
    return elements_dict


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

    atom_dict = reified_element_to_dict("atom_tuple", atoms)
    literal_dict = reified_element_to_dict("literal_tuple", literals)
    literal_dict_rev = reverse_dict(literal_dict)
    outputs_dict = reified_output_to_dict(outputs)

    normal_program = Program("")
    for rule in reified_rules:
        if rule.startswith("{"):
            element = rule.replace("{{rule(", "")[:-2]
        else:
            element = rule.replace("rule(", "")[:-1]
        head, body = element.split(", ")
        rule_head = []
        rule_body = []
        if "disjunction" in head:
            head = head.replace("disjunction(", "")[:-1]
            if head in atom_dict:
                for atom_id in atom_dict[head]:
                    if atom_id in literal_dict_rev:
                        variable_id = literal_dict_rev[atom_id]
                        variable = variable_name_from_literal(
                            outputs_dict, variable_id)
                        if variable is not None:
                            rule_head.append(variable)
        if "choice" in head:
            head = head.replace("choice(", "")[:-1]
            if head in atom_dict:
                for atom_id in atom_dict[head]:
                    if atom_id in literal_dict_rev:
                        variable_id = literal_dict_rev[atom_id]
                        variable = variable_name_from_literal(
                            outputs_dict, variable_id)
                        if variable is not None:
                            rule_head.append(f"{{{variable}}}")
        body = body.replace("normal(", "")[:-1]
        if body in literal_dict:
            for body_id in literal_dict[body]:
                negated = False
                if body_id.startswith("-"):
                    body_id = body_id.replace("-", "")
                    negated = True
                variable_id = literal_dict_rev[body_id]
                variable = variable_name_from_literal(
                    outputs_dict, variable_id)
                if variable is not None:
                    if negated:
                        variable = "not " + variable
                    rule_body.append(variable)
        if len(rule_head) + len(rule_body) == 0:
            continue
        if len(rule_body) == 0:
            normal_program.add_rule((f"{' | '.join(rule_head)}."))
        else:
            normal_program.add_rule(
                (f"{' | '.join(rule_head)} :- {', '.join(rule_body)}."))
    return normal_program
