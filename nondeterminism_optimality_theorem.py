import itertools
import gurobipy as gp
from gurobipy import GRB
gp.Model()


def assert_equal(*a):
    x = a[0]
    for y in a:
        if x != y:
            raise Exception("Elements were not equal.")
    return x


def normalize_to_stochastic_matrix(m):
    to_return = []
    for row in m:
        s = sum(row)
        if s == 1:
            to_return.append(row.copy())
        else:
            new_row = []
            for i in range(len(row)):
                new_row.append(row[i] / s)
            to_return.append(new_row)
    return to_return



def lin_sum(index_list, term_function):
    to_return = gp.LinExpr()
    for index in index_list:
        to_return += term_function(index)
    return to_return


def optimal_contract(c, d, q_0, q, i_star, allow_commitment=False, force_binary_p=False, \
                     ts_constraint=False, extra_constraints=[]):
    vtype = GRB.BINARY if force_binary_p else GRB.CONTINUOUS
    ell = assert_equal(len(d), len(q_0[0]), len(q[0]))
    m = [len(q[0][k]) for k in range(ell)]
    n = assert_equal(len(c), len(q_0), len(q))
    q_0 = normalize_to_stochastic_matrix(q_0)
    q = [normalize_to_stochastic_matrix(q_i) for q_i in q]
    best_obj = GRB.INFINITY
    best = None, [], [], []
    for p_is_zero in ([[0]*ell] if allow_commitment else itertools.product(range(2), repeat=ell)):
        #print(p_is_zero)
        model = gp.Model()
        model.Params.LogToConsole = 0
        model.params.NonConvex = 2
        p = [0 if p_is_zero[k] else model.addVar(lb=0, ub=1, vtype=vtype, \
             name=f"p_{k}") for k in range(ell)]
        t = [[model.addVar(lb=(-GRB.INFINITY if p_is_zero[k] else 0)) \
              for j in range(m[k])] for k in range(ell)]
        s = [model.addVar(lb=0, vtype=GRB.CONTINUOUS) if allow_commitment else \
             d[k] + lin_sum(range(m[k]), lambda j: q[i_star][k][j]*t[k][j]) for k in range(ell)]
        for k in range(ell):
            if p_is_zero[k]:
                model.addConstr(s[k] >= 0, name=f"s_positive_{k}")
        for i_prime in range(n):
            if i_prime != i_star:
                model.addQConstr(-c[i_star] + lin_sum(range(ell), lambda k: q_0[i_star][k] * \
                # This line simplifies the next two lines, but only works in no-commitment variant
                             #(s[k] - p[k]*d[k])) >= \
                             ((1 - p[k])*s[k] + p[k]*lin_sum(range(m[k]), \
                             lambda j: q[i_star][k][j]*t[k][j]))) >= \
                             -c[i_prime] + lin_sum(range(ell), lambda k: q_0[i_prime][k] * \
                             ((1 - p[k])*s[k] + p[k]*lin_sum(range(m[k]), \
                             lambda j: q[i_prime][k][j]*t[k][j]))), name=f"ic_{i_prime}")
        if ts_constraint:
            for k in range(ell):
                if not p_is_zero[k]:
                    for j in range(m[k]):
                        model.addConstr(t[k][j] <= s[k])
        if allow_commitment:
            expected_cost = lin_sum(range(ell), lambda k: q_0[i_star][k] * \
                             ((1 - p[k])*s[k] + p[k]*(d[k] + lin_sum(range(m[k]), \
                             lambda j: q[i_star][k][j]*t[k][j]))))
        else:  # Another similar simplification, could just use the objective function above
            expected_cost = lin_sum(range(ell), lambda k: q_0[i_star][k] * s[k])
        for constraint in extra_constraints:
            model.addConstr(eval(constraint))
        model.setObjective(expected_cost, GRB.MINIMIZE)
        model.optimize()
        if model.Status != GRB.OPTIMAL:
            pass
            #print(f"Model optimization status: {model.Status}")
            #return None
        elif model.objVal < best_obj:
            best_obj = model.objVal
            pp = []
            for y in p:
                if type(y) == int:
                    pp.append(0)
                else:
                    pp.append(y.x)
            ss = [y.x for y in s] if allow_commitment else [y.getValue() for y in s]
            best = model.objVal, pp, ss, [[y.x for y in row] for row in t]
    return best


if __name__ == '__main__':
    c = [0, 0, 1]
    d = [1, 1]
    q_0 = [[1, 1], [3, 2], [3, 2]]
    q = [[[3, 2], [3, 2]], [[2, 3], [2, 3]], [[3, 2], [3, 2]]]
    i_star = 2
    for deterministic in [False, True]:
        for variant, ac, ts in [
            ["CoMI", True, False],
            ["UMI", False, False],
            ["CoNI", True, True],
            ["UNI", False, True],
        ]:
            min_pay, p, s, t = optimal_contract(c, d, q_0, q, i_star, allow_commitment=ac, \
                                                ts_constraint=ts, force_binary_p=deterministic)
            print(f"\nOptimal contract in {variant}{', deterministic' if deterministic else ''}:")
            print(min_pay)
            print(p)
            print(s)
            print(t)

