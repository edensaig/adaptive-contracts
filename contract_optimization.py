import numpy as np
import cvxpy as cp

class LPContractOptimizer:
    solver_params = {}
    
    @classmethod
    def objective(cls,*,F,t,**kwargs):
        raise NotImplemented

    @classmethod
    def constraints(cls,F,c,t,monotone):
        '''
        :param F: size nxm numpy ndarray of outcome distributions
        :param c: size n numpy array of costs
        :param t: size m numpy array of contract transfers
        :param monotone: Flag indicating that the monotonicity constraint must be enforced
        :return: A list of constraints
        '''
        out = [
            (F[-1] - F[:-1])@t >= c[-1]-c[:-1],
            t>=0,
        ]
        if monotone:
            out.append(t[:-1]<=t[1:])
        return out
        
    @classmethod
    def solve(cls,*,F,c,target,monotone=False,**kwargs):
        n,m = F.shape
        F.copy()
        F[[target,-1]] = F[[-1,target]]
        c = c.copy()
        c[[target,-1]] = c[[-1,target]]
        t = cp.Variable(m)
        obj = cls.objective(F=F,t=t,**kwargs)
        constraints = cls.constraints(F,c,t,monotone)
        prob = cp.Problem(cp.Minimize(obj), constraints)
        prob.solve(**cls.solver_params)
        t_opt = t.value
        # t_opt = t_opt - t_opt.min() if t_opt is not None else None
        return t.value, obj.value


class MinPayOptimizer(LPContractOptimizer):
    solver_params = {'solver': cp.CLARABEL}
    
    @classmethod
    def objective(cls,*,F,t):
        return F[-1]@t


class DiscreteInspectionContractOptimizer:
    @classmethod
    def build_F(cls,*,q0,q,p):
        n,l = q0.shape
        m = [qk.shape[1] for qk in q]
        F = np.zeros((n,sum(m[k] if p[k] else 1 for k in range(l))))+10
        j = 0
        for k in range(l):
            if p[k]==1:
                F[:,j:j+m[k]] = np.tile(q0[:,k],(m[k],1)).T*q[k]
                j += m[k]
            elif p[k]==0:
                F[:,j] = q0[:,k]
                j += 1
            else:
                raise RuntimeError
        assert j == F.shape[1]
        assert np.isclose(F.sum(axis=1),1).all()
        return F

    @classmethod
    def solve_for_fixed_p(cls,*,q0,q,c,d,p,target):
        """
        q0 - np.array, q0.shape=(n_actions, l_signals)
        q - list of np.array, q[k].shape=(n_actions, mk_outcomes)
        c - np.array of action costs, c.shape=(n_actions), c>=0
        d - np.array of inspection costs, d.shape=(l_signals), d>=0
        p - np.array of inspection policy, p.shape=(l_signals), p[k] in [0,1]
        target - target action, integer
        """
        F = cls.build_F(q0=q0, q=q, p=p)
        combined_t, minpay_obj = MinPayOptimizer.solve(F=F,c=c,target=target)
        if minpay_obj is None:
            raise RuntimeError('Optimal contract not found')
        obj = minpay_obj + (p*q0[target])@d
        return combined_t, obj
    
