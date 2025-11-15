

# Contrastive Explanations for ASP

This project contains the implementation of the Master's Thesis "Contrastive Explanations for ASP".
Eiter et al.[^1] formalized contrastive explanations for ASP. This formalization forms the theoretical framework
for this project.

The main goal of the thesis is to determine the practical feasibility of applying the theoretical approach of 
contrastive explanations to ASP. To achieve this, this project was created, consisting of a naive grounder, a backend,
which follows the definitions provided by Eiter et al., and a user-friendly interface.

# Getting Started
## Dependencies
- PySide6 V6.10
- Clingo V5.8
## Executing program
```bash 
pip install -r requirements.txt
```
```bash
python.exe ui.py
```


# License
This project is licensed under the MIT License - see the LICENSE.md file for details

[^1]:Eiter, Thomas, et al. ‘Contrastive Explanations for Answer-Set Programs’. European Conference on Logics in Artificial Intelligence, Springer, 2023, pp. 73–89.
