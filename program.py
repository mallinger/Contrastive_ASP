"""
Program Module

This module is used to represent answer set programs as Rule and Program objects.
"""

from copy import deepcopy
import re
from utils import (
    elements_from_body_or_predicate,
    verify_head_formating,
    verify_comma_placement,
    are_choice_atoms_equal,
    choice_literal_of_rule,
    unfold_choice_atom_to_ordered_string,
    parse_choice_atom,
    clean_head,
    clean_body,
    clean_literal,
    clean_atom,
)



class Program:
    """
    This class is used to represent an answer set program.
    
    The rules are stored in the set variable "rules".
    
    Parameters
    ----------
    prg : str or set of Rule
        If a string, it must represent a program where rules are terminated by
        periods ("."). If a set, it must contain only `Rule`
        instances.
    """
    def __init__(self, prg):
        if isinstance(prg, str):
            if prg != "" and not prg.strip().endswith("."):
                raise SyntaxError("Program does not end with '.'")
            prg = prg.strip()
            self.rules = set(
                [
                    Rule(f"{rule.lstrip()}.")
                    for rule in re.split(r"\.\s+", prg[:-1])
                    if rule.strip() != ""
                ]
            )
        elif isinstance(prg, set) and all(isinstance(r, Rule) for r in prg):
            self.rules = prg
        else:
            raise ValueError(
                f"Program constructor argument needs to be a String or set of Rules, not {type(prg)}."
            )

    def __repr__(self):
        return " ".join(str(r) for r in self.rules)

    def __sub__(self, other):
        """
        Returns a new Program object containing the rules present in this program but
        not in the given one.
        """
        return Program(self.rules - other.rules)

    def __add__(self, other):
        """
        Returns a new Program object containing the rules present in both this program and
        a the given one.
        """
        return Program(self.rules | other.rules)

    def __eq__(self, other):
        """
        Test equality between two Program instances.
        """
        if not isinstance(other, Program):
            return False
        return self.rules == other.rules

    def add_rule(self, rule):
        """
        Add a rule to the program.
        
        Parameters
        ----------
        rule : Rule or str
            Either a `Rule` instance or a string representation of a rule.
            If a string is provided, it will be converted to a `Rule`.
        """
        if isinstance(rule, Rule):
            self.rules.add(rule)
        else:
            self.rules.add(Rule(rule))

    def remove_rule(self, rule):
        """
        Remove a rule from the program.
        """
        self.rules.remove(rule)

    def add_program(self, program):
        """
        Add all rules of a given program to this program.
        """
        self.rules = self.rules.union(program.rules)
        return self

    def __hash__(self):
        return sum([hash(r) for r in self.rules])

    def intersection(self, other):
        """
        Return the intersection of a given program with this program 
        """
        return Program(self.rules & other.rules)

    def contains_atom(self, atom):
        """
        Checks whether any rule in the program contains a given atom. 
        """
        return any(r.contains_atom(atom) for r in self.rules)


class Rule:
    """
    This class is used to represent an answer set programming rule.
    
    The rule is represented as two lists, one for the head atoms and
    one for the body literals.
    
    Parameters
    ----------
    rule_str : str
        The rule in string format. It must end with a period (".").
        
    """
    def __init__(self, rule_str):
        try:
            verify_comma_placement(rule_str)
        except SyntaxError as e:
            raise SyntaxError(f'{e} at rule "{rule_str}"') from e

        if ":-" not in rule_str:
            head = rule_str[:-1].split("|")
            self.body = []
            try:
                verify_head_formating(head)
                self.head = clean_head(head)
            except SyntaxError as e:
                raise SyntaxError(f'{e} at rule "{rule_str}"') from e
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
                    raise SyntaxError(f'{e} at rule "{rule_str}"') from e
            try:
                body = elements_from_body_or_predicate(body)
                self.body = clean_body(body)
            except SyntaxError as e:
                raise SyntaxError(f'{e} at rule "{rule_str}"') from e

    def __lt__(self, other):
        """
        Compare two rules for ordering.
        
        The ordering prioritizes:
        1. Facts before non-facts.
        2. Non-constraints before constraints.
        3. Otherwise, rules with fewer total literals.
        """
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
        """
        Add a literal to the body of the rule.
        """
        self.body.append(clean_literal(literal))

    def remove_literal(self, literal):
        """
        Remove a literal from the body of the rule.
        """
        self.body.remove(clean_literal(literal))

    def is_fact(self):
        """
        Check whether the rule is a fact.
        """
        return self.body == []

    def is_constraint(self):
        """
        Check whether the rule is a constraint.
        """
        return self.head == []

    def is_choice(self):
        """
        Check whether the rule is a choice rule.
        """
        if len(self.head) != 1:
            return False
        return self.head[0].startswith("{")

    def contains_choice(self):
        """
        Check whether the rule contains any choice literals.
        """
        if self.is_choice():
            return True
        for literal in self.body:
            if literal.replace("not ", "").startswith("{"):
                return True
        return False

    def contains_atom(self, atom):
        """
        Check whether the rule contains a given atom.
        """
        atom = clean_atom(atom)
        if atom in self.head:
            return True
        for literal in self.body:
            if atom in literal.replace("not ", ""):
                return True
        if self.is_choice():
            choice_elements, _, _ = parse_choice_atom(self.head[0])
            if any(
                [atom.replace(" ", "") == c.replace(" ", "") for c in choice_elements]
            ):
                return True
        return False

    def __eq__(self, other):
        """
        Check whether the rule is equal to another. 
        Order of literals is irrelevant for equality.
        """
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
        return sorted(self.head) == sorted(other.head) and sorted(self.body) == sorted(
            other.body
        )

    def __hash__(self):
        if self.is_choice():
            return hash(unfold_choice_atom_to_ordered_string(self.head[0])) + hash(
                f"{sorted(self.body)}"
            )

        if self.contains_choice():
            choice_literal = choice_literal_of_rule(self.body)
            self_without_choice = deepcopy(self)
            self_without_choice.remove_literal(choice_literal)
            return hash(unfold_choice_atom_to_ordered_string(choice_literal)) + hash(
                self_without_choice
            )

        if self.is_fact():
            return hash(f"{sorted(self.head)}")

        return hash(f"{sorted(self.head)} :- {sorted(self.body)}")
