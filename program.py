from copy import deepcopy
from utils import literals_from_body, verify_head_formating, verify_comma_placement, are_choice_atoms_equal, choice_literal_of_rule, unfold_choice_atom_to_ordered_string, parse_choice_atom, clean_head, clean_body, clean_literal, clean_atom
import re

class Program:

    def __init__(self, prg):
        if isinstance(prg, str):
            if prg != "" and not prg.strip().endswith("."):
                raise SyntaxError("Program does not end with '.'")
            prg = prg.strip()
            self.rules = set([Rule(f"{rule.lstrip()}.")
                             for rule in re.split(r"\.\s+", prg[:-1]) if rule.strip() != ""])
        elif isinstance(prg, set) and all(isinstance(r, Rule) for r in prg):
            self.rules = prg
        else:
            raise ValueError(f"Program constructor argument needs to be a String or set of Rules, not {type(prg)}.")

    def __repr__(self):
        return " ".join(str(r) for r in self.rules)

    def __sub__(self, other):
        return Program(self.rules - other.rules)

    def __add__(self, other):
        return Program(self.rules | other.rules)

    def __eq__(self, other):
        if not isinstance(other, Program):
            return False
        return self.rules == other.rules

    def add_rule(self, rule):
        if isinstance(rule, Rule):
            self.rules.add(rule)
        else:
            self.rules.add(Rule(rule))

    def remove_rule(self, rule):
        self.rules.remove(rule)

    def add_program(self, program):
        self.rules = self.rules.union(program.rules)
        return self

    def fact_to_choice(self, fact):
        self.remove_rule(fact)
        head = ' | '.join(fact.head)
        self.rules.add(Rule(f"{{{head}}}."))

    def __hash__(self):
        return sum([hash(r) for r in self.rules])

    def intersection(self, other):
        return Program(self.rules & other.rules)

    def contains_atom(self, atom):
        return any(r.contains_atom(atom) for r in self.rules)


class Rule:
    def __init__(self, rule_str):
        try:
            verify_comma_placement(rule_str)
        except SyntaxError as e:
            raise SyntaxError(f"{e} at rule \"{rule_str}\"") from e
        
        if ":-" not in rule_str:
            head = rule_str[:-1].split("|")
            self.body = []
            try:
                verify_head_formating(head)
                self.head = clean_head(head)
            except SyntaxError as e:
                raise SyntaxError(f"{e} at rule \"{rule_str}\"") from e
        else:
            head, body = rule_str[:-1].split(":-")
            if head.strip() == "":
                self.head = []
            else:
                head = head.split("|")
                try:
                    verify_head_formating(head)
                    self.head = clean_head(head)
                except SyntaxError as e:
                    raise SyntaxError(f"{e} at rule \"{rule_str}\"") from e
            try:
                body = literals_from_body(body)
                self.body = clean_body(body)
            except SyntaxError as e:
                raise SyntaxError(f"{e} at rule \"{rule_str}\"") from e

    def __lt__(self, other):
        if self.is_fact() and not other.is_fact():
            return True
        if self.is_constraint() and not other.is_constraint():
            return False
        if not self.is_constraint() and other.is_constraint():
            return True
        return len(self.head) + len(self.body) < len(other.head) + len(other.body)

    def __repr__(self):
        if self.is_fact():
            return f"{' | '.join(self.head)}."
        return f"{' | '.join(self.head)} :- {', '.join(self.body)}."

    def add_literal(self, literal):
        self.body.append(clean_literal(literal))

    def remove_literal(self, literal):
        self.body.remove(clean_literal(literal))

    def is_fact(self):
        return self.body == []

    def is_constraint(self):
        return self.head == []

    def is_choice(self):
        if len(self.head) != 1:
            return False
        return self.head[0].startswith("{")

    def contains_choice(self):
        if self.is_choice():
            return True
        for literal in self.body:
            if literal.replace("not ", "").startswith("{"):
                return True
        return False

    def contains_atom(self, atom):
        atom = clean_atom(atom)
        if atom in self.head:
            return True
        for literal in self.body:
            if atom in literal.replace("not ",""):
                return True
        if self.is_choice():
            choice_elements, _, _ = parse_choice_atom(self.head[0])
            if any([atom.replace(" ","") == c.replace(" ","") for c in choice_elements]):
                return True
        return False

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False

        if self.is_choice() and other.is_choice():
            if not are_choice_atoms_equal(self.head[0], other.head[0]):
                return False
            return sorted(self.body) == sorted(other.body)

        if self.contains_choice() and other.contains_choice():
            choice_literal = choice_literal_of_rule(self.body)
            choice_literal_other = choice_literal_of_rule(other.body)
            if not are_choice_atoms_equal(choice_literal, choice_literal_other):
                return False

            self_without_choice = deepcopy(self)
            self_without_choice.remove_literal(choice_literal)
            other_without_choice = deepcopy(other)
            other_without_choice.remove_literal(choice_literal_other)
            return self_without_choice == other_without_choice
        return sorted(self.head) == sorted(other.head) and sorted(self.body) == sorted(other.body)

    def __hash__(self):
        if self.is_choice():
            return hash(unfold_choice_atom_to_ordered_string(self.head[0])) + hash(f"{sorted(self.body)}")

        if self.contains_choice():
            choice_literal = choice_literal_of_rule(self.body)
            self_without_choice = deepcopy(self)
            self_without_choice.remove_literal(choice_literal)
            return hash(unfold_choice_atom_to_ordered_string(choice_literal)) + hash(self_without_choice)

        if self.is_fact():
            return hash(f"{sorted(self.head)}")

        return hash(f"{sorted(self.head)} :- {sorted(self.body)}")
