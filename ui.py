import sys
import json
from PySide6.QtWidgets import QCompleter, QMessageBox, QFileDialog, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QLineEdit, QTextEdit, QMenu
from PySide6.QtGui import QTextCharFormat, QColor
from PySide6.QtCore import Qt

from contrastive_explanation import contrastive_explanations

from grounder import ground
from program import Program, Rule
from utils import predicates_of_program

LABEL_STYLE = "font-weight: bold; font-size: 16px"
LABEL_STYLE_RED = "font-weight: bold; font-size: 16px; color: red"
BUTTON_STYLE = "font-weight: bold; font-size: 14px"
TEXT_FORMAT_RED = QTextCharFormat()
TEXT_FORMAT_RED.setForeground(QColor("red"))
TEXT_FORMAT_WHITE = QTextCharFormat()
TEXT_FORMAT_WHITE.setForeground(QColor("white"))


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(900, 600)
        self.setWindowTitle('Contrastive Explanations for ASP')

        self.program = Program("")
        self.S = Program("")
        self.selected_rules_dict = {}
        self.predicates = []

        # left elements
        program_label = QLabel(text="Program:")
        program_label.setStyleSheet(LABEL_STYLE)
        add_program_button = QPushButton(text="Add Program")
        add_program_button.setStyleSheet(BUTTON_STYLE)
        add_program_button.clicked.connect(self.add_program)
        add_program_layout = QHBoxLayout()
        add_program_layout.addWidget(program_label)
        add_program_layout.addWidget(add_program_button)
        self.program_edit = QTextEdit()
        self.program_edit.textChanged.connect(self.program_edit_changed)
        self.rules_select_layout = QVBoxLayout()

        # middle elements
        config_label = QLabel(text="Configuration:")
        config_label.setStyleSheet(LABEL_STYLE)
        add_config_button = QPushButton(text="Add Configuration")
        add_config_button.setStyleSheet(BUTTON_STYLE)
        add_config_button.clicked.connect(self.add_config)
        add_config_layout = QHBoxLayout()
        add_config_layout.addWidget(config_label)
        add_config_layout.addWidget(add_config_button)

        S_label = QLabel(text="S:")
        S_label.setStyleSheet(LABEL_STYLE)
        self.S_edit = QTextEdit()
        self.S_edit.textChanged.connect(self.S_edit_text_changed)

        assumption_label = QLabel(text="Assumptions:")
        assumption_label.setStyleSheet(LABEL_STYLE)
        self.assumption_menu_button = QPushButton(text="Add Assumption")
        self.assumption_menu = QMenu()
        self.assumption_menu_button.setMenu(self.assumption_menu)
        assumption_layout = QHBoxLayout()
        assumption_layout.addWidget(assumption_label)
        assumption_layout.addWidget(self.assumption_menu_button)
        self.assumptions_edit = QLineEdit()

        self.explanandum_label = QLabel(text="Explanandum:")
        self.explanandum_label.setStyleSheet(LABEL_STYLE)
        self.explanandum_menu_button = QPushButton(text="Add Explanandum")
        self.explanandum_menu = QMenu()
        self.explanandum_menu_button.setMenu(self.explanandum_menu)
        explanandum_layout = QHBoxLayout()
        explanandum_layout.addWidget(self.explanandum_label)
        explanandum_layout.addWidget(self.explanandum_menu_button)
        self.explanandum_edit = QLineEdit()
        self.explanandum_edit.textChanged.connect(
            self.explanandum_text_changed)

        self.foil_label = QLabel(text="Foil:")
        self.foil_label.setStyleSheet(LABEL_STYLE)
        self.foil_menu_button = QPushButton(text="Add Foil")
        self.foil_menu = QMenu()
        self.foil_menu_button.setMenu(self.foil_menu)
        foil_layout = QHBoxLayout()
        foil_layout.addWidget(self.foil_label)
        foil_layout.addWidget(self.foil_menu_button)
        self.foil_edit = QLineEdit()
        self.foil_edit.textChanged.connect(self.foil_text_changed)

        interpretation_label = QLabel(text="Interpretation:")
        interpretation_label.setStyleSheet(LABEL_STYLE)
        self.interpretation_edit = QTextEdit()

        # right elements
        start_button = QPushButton(text="Go!")
        start_button.setStyleSheet(LABEL_STYLE)
        start_button.clicked.connect(self.go)
        result_label = QLabel(text="Contrastrive Explanations:")
        result_label.setStyleSheet(LABEL_STYLE)
        self.result_edit = QTextEdit()
        reset_button = QPushButton(text="Reset")
        reset_button.setStyleSheet(LABEL_STYLE)
        reset_button.clicked.connect(self.reset)

        # layouts
        outer_box = QHBoxLayout()
        self.left_box = QVBoxLayout()
        middle_box = QVBoxLayout()
        right_box = QVBoxLayout()

        self.left_box.addLayout(add_program_layout)
        self.left_box.addWidget(self.program_edit)
        self.left_box.addLayout(self.rules_select_layout)

        middle_box.addLayout(add_config_layout)
        middle_box.addWidget(S_label)
        middle_box.addWidget(self.S_edit)
        middle_box.addLayout(assumption_layout)
        middle_box.addWidget(self.assumptions_edit)
        middle_box.addLayout(explanandum_layout)
        middle_box.addWidget(self.explanandum_edit)
        middle_box.addLayout(foil_layout)
        middle_box.addWidget(self.foil_edit)
        middle_box.addWidget(interpretation_label)
        middle_box.addWidget(self.interpretation_edit)
        middle_box.addStretch()

        right_box.addWidget(start_button)
        right_box.addWidget(result_label)
        right_box.addWidget(self.result_edit)
        right_box.addWidget(reset_button)

        outer_box.addLayout(self.left_box)
        outer_box.addLayout(middle_box)
        outer_box.addLayout(right_box)
        self.setLayout(outer_box)

    def go(self):
        P = self.program_edit.toPlainText()
        try:
            program = ground(P.replace("\n"," "))
        except SyntaxError as syntax_error:
            msg = QMessageBox()
            msg.setText("Error")
            msg.setInformativeText(str(syntax_error))
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
            return
        S = self.S_edit.toPlainText()
        A = self.assumptions_edit.text().split(",")
        I = self.interpretation_edit.toPlainText().split(", ")
        E = self.explanandum_edit.text().strip().split(",")
        F = self.foil_edit.text().strip().split(",")
        print(f"""Go called with program:{P}
              S: {S}
              Assumptions: {A}
              Interpretation: {I}
              Explanandum: {E}
              Foil: {F}
              """)
        if E == ['']:
            self.explanandum_label.setStyleSheet(LABEL_STYLE_RED)
            return
        if F == ['']:
            self.foil_label.setStyleSheet(LABEL_STYLE_RED)
            return
        try:
            CEs = contrastive_explanations(
                (program, Program(S), A), (I, E, F))
            CEs_str = list(map(str, CEs))
            self.result_edit.setText("\n\n".join(CEs_str))
        except ValueError as error:
            self.result_edit.setText(str(error))

    def reset(self):
        self.program = Program("")
        self.program_edit.setText("")
        self.S = Program("")
        self.S_edit.setText("")
        self.assumptions_edit.setText("")
        self.assumption_menu.clear()
        self.explanandum_edit.setText("")
        self.explanandum_menu.clear()
        self.interpretation_edit.setText("")
        self.foil_edit.setText("")
        self.foil_menu.clear()
        self.predicates = []

        self.result_edit.setText("")
        self.selected_rules_dict = {}

        deleteItemsOfLayout(self.rules_select_layout)

    def update_autocomplete(self, words):
        autocomplete = QCompleter(words)
        autocomplete.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.assumptions_edit.setCompleter(autocomplete)
        self.explanandum_edit.setCompleter(autocomplete)
        self.foil_edit.setCompleter(autocomplete)

    def add_program(self):
        path_to_file, _ = QFileDialog.getOpenFileName()

        if path_to_file == '':
            return
        with open(path_to_file, 'r', encoding='utf-8') as file:
            program_str = file.read().strip()
            faulty_rules = []
            for rule in program_str[:-1].split(". "):
                try:
                    r = Rule(f"{rule}.")
                    self.program.add_rule(r)
                except SyntaxError:
                    faulty_rules.append(rule)

            self.program_edit.setText(str(self.program).replace(". ", ".\n"))

            self.predicates = predicates_of_program(self.program)
            self.update_autocomplete(self.predicates)

            self.update_menus()
            self.add_selected_rules_layouts()

    def update_menus(self):
        for predicate in self.predicates:
            self.assumption_menu.addAction(
                predicate, lambda x=predicate: self.add_assumption(x))
            self.explanandum_menu.addAction(
                predicate, lambda x=predicate: self.add_explanandum(x))
            self.foil_menu.addAction(
                predicate, lambda x=predicate: self.add_foil(x))

    def add_selected_rules_layouts(self):
        for rule in self.program.rules:
            rule_hbox = QHBoxLayout()
            rule_s_button = QPushButton(text="S")
            rule_edit = QLineEdit(text=str(rule))
            rule_s_button.clicked.connect(
                lambda _, x=rule, y=rule_edit: self.s_selected(x, y))

            rule_hbox.addWidget(rule_s_button)
            rule_hbox.addWidget(rule_edit)
            self.selected_rules_dict[rule] = rule_edit
            self.rules_select_layout.addLayout(rule_hbox)

    def add_config(self):
        path_to_file, _ = QFileDialog.getOpenFileName()
        if path_to_file == '':
            return
        with open(path_to_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
        self.S = Program(config["S"])
        self.S_edit.setText(str(self.S))
        self.update_S_selection_layouts()
        self.assumptions_edit.setText(", ".join(config["A"]))
        self.interpretation_edit.setText(", ".join(config["I"]))
        self.explanandum_edit.setText(", ".join(config["E"]))
        self.foil_edit.setText(", ".join(config["F"]))
        

    def program_edit_changed(self):
        try:
            new_program = Program(self.program_edit.toPlainText())
            if new_program != self.program:
                self.program = new_program
                self.update_ui()
        except:
            pass

    def update_ui(self):
        self.predicates = predicates_of_program(self.program)
        self.assumption_menu.clear()
        self.explanandum_menu.clear()
        self.foil_menu.clear()
        for predicate in self.predicates:
            self.assumption_menu.addAction(
                predicate, lambda x=predicate: self.add_assumption(x))
            self.explanandum_menu.addAction(
                predicate, lambda x=predicate: self.add_explanandum(x))
            self.foil_menu.addAction(
                predicate, lambda x=predicate: self.add_foil(x))
            
        deleteItemsOfLayout(self.rules_select_layout)
        self.add_selected_rules_layouts()

    def s_selected(self, rule, rule_edit):
        if rule in self.S.rules:
            self.S.remove_rule(rule)
            rule_edit.setStyleSheet("color: white;")
        else:
            self.S.add_rule(rule)
            rule_edit.setStyleSheet("font-weight: bold")
        self.S_edit.setText(str(self.S))

    def update_S_selection_layouts(self):
        for rule, rule_edit in self.selected_rules_dict.items():
            if rule in self.S.rules:
                rule_edit.setStyleSheet("font-weight: bold")
            else:
                rule_edit.setStyleSheet("color: white;")

    def add_assumption(self, predicate):
        current_assumptions = self.assumptions_edit.text().split(", ")

        if predicate in current_assumptions:
            current_assumptions.remove(predicate)
        else:
            current_assumptions.append(predicate)
        if '' in current_assumptions:
            current_assumptions.remove('')
        self.assumptions_edit.setText(", ".join(current_assumptions))

    def add_explanandum(self, predicate):
        current_explanandum = self.explanandum_edit.text().split(", ")
        if predicate in current_explanandum:
            current_explanandum.remove(predicate)
        else:
            current_explanandum.append(predicate)

        if '' in current_explanandum:
            current_explanandum.remove('')
        self.explanandum_edit.setText(", ".join(current_explanandum))

    def add_foil(self, predicate):
        current_foil = self.foil_edit.text().split(", ")
        if predicate in current_foil:
            current_foil.remove(predicate)
        else:
            current_foil.append(predicate)
        if '' in current_foil:
            current_foil.remove('')
        self.foil_edit.setText(", ".join(current_foil))

    def S_edit_text_changed(self):
        try:
            new_program = Program(self.S_edit.toPlainText())
            if new_program != self.S:
                self.S = new_program
                self.update_S_selection_layouts()
        except:
            pass

    def explanandum_text_changed(self):
        if self.explanandum_edit.text != "":
            self.explanandum_label.setStyleSheet(LABEL_STYLE)

    def foil_text_changed(self):
        if self.foil_edit.text != "":
            self.foil_label.setStyleSheet(LABEL_STYLE)


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())


if __name__ == '__main__':
    main()
