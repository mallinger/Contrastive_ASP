from utils import literals_from_body, verify_head_formating


class Program:

    def __init__(self, prg):
        if isinstance(prg, str):
            if prg != "" and not prg.strip().endswith("."):
                raise SyntaxError("Program does not end with '.'")
            self.rules = set([Rule(f"{rule.lstrip()}.")
                             for rule in prg[:-1].split(".") if rule.strip() != ""])
        elif isinstance(prg, set) and all(isinstance(r, Rule) for r in prg):
            self.rules = prg
        else:
            raise ValueError(f"Program constructor argument needs to be a String or list of Rules, not {type(prg)}.")

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


class Rule:
    def __init__(self, rule_str):
        if ":-" not in rule_str:
            head = rule_str[:-1].split("|")
            self.head = list(map(str.strip, head))
            self.body = []
        else:
            head, body = rule_str[:-1].split(":-")
            if head.strip() == "":
                self.head = []
            else:
                head = head.split("|")
                try:
                    verify_head_formating(head)
                    self.head = list(map(str.strip, head))
                except SyntaxError as e:
                    raise SyntaxError(f"{e} at rule \"{rule_str}\"") from e
            try:
                self.body = literals_from_body(body)
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
        self.body.append(literal)

    def remove_literal(self, literal):
        self.body.remove(literal)

    def is_fact(self):
        return self.body == []

    def is_constraint(self):
        return self.head == []

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
        return sorted(self.head) == sorted(other.head) and sorted(self.body) == sorted(other.body)

    def __hash__(self):
        if self.is_fact():
            return hash(f"{sorted(self.head)}")
        return hash(f"{sorted(self.head)} :- {sorted(self.body)}")
