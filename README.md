# Adaptive Contracts for Cost-Effective AI Delegation

Comments are welcome! 🙂

Environment setup: `conda create -n adaptivecontracts anaconda conda-forge::cvxpy`.

Our empirical analysis in `alpacaeval.ipynb` and `swebench.ipynb` relies on AlpacaEval and SWE-Bench data, which can be fetched using the script `fetch_data.sh`.

Our numerical validation in `nondeterminism_optimality_theorem.py` (strictly optimal nondeterministic inspection for UMI and CoNI) relies on the Gurobi optimizer, which can be installed using `conda install gurobi::gurobiconda`.
