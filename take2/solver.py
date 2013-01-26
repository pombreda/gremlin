from linsys import LinSys, FreeVar, LinVar, BinExpr


class RecEvalDict(object):
    __slots__ = ["rec_eval"]
    def __init__(self, rec_eval):
        self.rec_eval = rec_eval
    def __getitem__(self, key):
        return self.rec_eval(key)

class ConstraintSolver(object):
    def __init__(self, root):
        self.root = root
        self.linsys = LinSys(list(self.root.get_constraints()))
        freeness_relation = [None, "user", "offset", "cons", "padding", "default", "input"]
        var_order = sorted(self.linsys.get_vars(), key = lambda v: freeness_relation.index(v.type))
        self.solution = self.linsys.solve(var_order)
        for var in self.get_freevars():
            if var.type == "padding":
                self.solution[var] = 0.0
        self.dependencies = self._calculate_dependencies()
        self.results = {}
        self.update({var : var.default for var in self.get_freevars() if var.default is not None})

    def __str__(self):
        return "\n".join("%s = %s" % (k, v) for k, v in self.solution.items()
            if not isinstance(v, FreeVar))
    def __getitem__(self, var):
        if var in self.results:
            return self.results[var]
        return self.solution[var]
    def __contains__(self, var):
        return var in self.results or var in self.solution

    def is_free(self, var):
        return isinstance(self.solution[var], FreeVar)
    def get_freevars(self):
        for k, v in self.solution.items():
            if isinstance(v, FreeVar):
                yield k

    def _get_equation_vars(self, expr):
        if isinstance(expr, (str, LinVar, FreeVar)):
            return {expr.name}
        elif isinstance(expr, BinExpr):
            return self._get_equation_vars(expr.lhs) | self._get_equation_vars(expr.rhs)
        else:
            return set()
    def _transitive_closure(self, deps):
        oldlen = -1
        while oldlen != len(deps):
            oldlen = len(deps)
            for resvar, expr in self.solution.items():
                depvars = self._get_equation_vars(expr)
                if deps & depvars:
                    deps.add(resvar)
    def _calculate_dependencies(self):
        dependencies = {}
        for var in self.get_freevars():
            dependencies[var] = {var}
            self._transitive_closure(dependencies[var])
        return dependencies

    def update(self, freevars):
        #prev_results = self.results.copy()
        for k in freevars.keys():
            if not self.is_free(k):
                raise ValueError("%r is not a free variable" % (k,))
            for k2 in self.dependencies[k]:
                self.results.pop(k2, NotImplemented)
        
        def rec_eval(key):
            if key in self.results:
                if self.results[key] is NotImplemented:
                    raise ValueError("Cyclic dependency found, var = %r" % (key,))
                return self.results[key]
            # set up sentinel to detect cycles
            self.results[key] = NotImplemented
            v = self.solution[key]
            if isinstance(v, FreeVar):
                if key not in freevars and key.default is not None:
                    self.results[key] = key.default
                else:
                    self.results[key] = freevars[key]
            elif hasattr(v, "eval"):
                self.results[key] = v.eval(rec_eval_dict)
            else:
                self.results[key] = v
            return self.results[key]

        rec_eval_dict = RecEvalDict(rec_eval)
        for k in self.solution:
            rec_eval(k)
        
        return self.results


if __name__ == "__main__":
    pass




