"""
genrel package for GR calculations
David Clark, Kai Smith, David Cyncynates
Case Western Reserve university
2014
"""

import numpy as np
import sympy as sp

#returns a rank 3 tensor that represents the symbols
#first index corresponds to the upper index
def christoffel_symbols(metric, metric_key):
    symbols = tensor(3)
    inverse = inverse_metric(metric)
    for alpha in range(4):
        for beta in range(4):
            for gamma in range(4):
                total = 0
                for delta in range(4):                    
                    total += inverse[alpha][delta] * (sp.diff(metric[delta][beta], metric_key[gamma])
                        + sp.diff(metric[delta][gamma], metric_key[beta])
                        - sp.diff(metric[beta][gamma], metric_key[delta]))
                symbols[alpha][beta][gamma] = sp.cancel(total/2)
    return symbols


#returns the rank 4 Reimann curvature tensor
#the first index corresponds to an upper index -- the rest are lower
def reimann_tensor(chris_sym, metric_key):
    reimann = tensor(4)
    for alpha in range(4):
        for beta in range(4):
            for gamma in range(4):
                for delta in range(4):
                    total = 0
                    total += sp.diff(chris_sym[alpha][beta][delta], metric_key[gamma])
                    total -= sp.diff(chris_sym[alpha][beta][gamma], metric_key[delta])
                    for epsilon in range(4):
                        total += chris_sym[alpha][gamma][epsilon]*chris_sym[epsilon][beta][delta]
                        total -= chris_sym[alpha][delta][epsilon]*chris_sym[epsilon][beta][gamma]
                    reimann[alpha][beta][gamma][delta] = sp.cancel(total)
    return reimann


#returns the rank 2 Ricci curvature tensor
#both indicies are lower
def ricci_tensor(reimann):
    ricci = tensor(2)
    for alpha in range(4):
        for beta in range(4):
            total = 0
            for gamma in range(4):
                total += reimann[gamma][alpha][gamma][beta]
            ricci[alpha][beta] = sp.cancel(total)
    return ricci

#returns the Ricci scalar, a sympy symbol
def ricci_scalar(ricci_t, metric):
    scalar = 0
    inverse = inverse_metric(metric)
    for alpha in range(4):
        for beta in range(4):
            scalar += inverse[alpha][beta] * ricci_t[alpha][beta]
    return sp.cancel(scalar)

#returns the rank 2 Einstein tensor
#both indices are lower
#think about whether you need to call raise_one_index before equating with a stress-energy tensor
def einstein_tensor(ricci_t, ricci_s, metric):
    einstein = tensor(2)
    for alpha in range(4):
        for beta in range(4):
            einstein[alpha][beta] = sp.cancel(ricci_t[alpha][beta] - 0.5*metric[alpha][beta]*ricci_s)
    return einstein

#runs through all parts of the program to find the Einstein tensor given only the metric and its key
def einstein_tensor_from_scratch(metric, metric_key):
    c_syms = christoffel_symbols(metric, metric_key)
    reimann_t = reimann_tensor(c_syms, metric_key)
    ricci_t = ricci_tensor(reimann_t)
    ricci_s = ricci_scalar(ricci_t, metric)
    return einstein_tensor(ricci_t, ricci_s, metric)

#returns expressions which, when set equal to zero, give the Einstein equations
def einstein_equations(einstein_tensor, stress_energy_tensor):
    einstein_equations = []
    for alpha in range(4):
        for beta in range(4):
            eq = sp.simplify(einstein_tensor[alpha][beta] - 8*sp.pi*sp.Symbol('G')*stress_energy_tensor[alpha][beta])
            if eq != 0 and eq not in einstein_equations:
                einstein_equations.append(eq)
    return einstein_equations

#returns a 4 x 4 x ... x 4 array of sympy symbols which represent a tensor
def tensor(rank):
    shape = [4 for i in range(rank)]
    return np.empty(shape, dtype = type(sp.Symbol('')))

#returns the rank of the tensor, passed in as a numpy array
def rank(tensor):
    return len(tensor.shape)

#returns the inverse of metric
def inverse_metric(metric):
    return np.array(sp.Matrix(metric).inv())

#matrix-multiplies the inverse metric and the tensor
#represents raising one index on a rank 2 tensor
def raise_one_index(tensor, metric, index = 1):
    return np.tensordot(inverse_metric(metric), tensor, index)

#matrix-multiplies the  metric and the tensor
#represents lowering one index on a rank 2 tensor
def lower_one_index(tensor, metric, index = 1):
    return np.tensordot(metric, tensor, index)

#prints a tensor (or a sympy scalar) in a readable form
def rprint(obj, position = []):
    if type(obj) != type(np.array([])):
        if obj != 0:
            sp.pprint(sp.simplify(obj))
    else:
        for n, entry in enumerate(obj):
            if type(entry) != type(np.array([])) and entry != 0:
                    print(str(position + [n]) + ": ")
                    sp.pprint(sp.simplify(entry))
            else:
                rprint(entry, position + [n])

#prints a tensor (or a sympy scalar) in LaTeX
def lprint(obj, position = []):
    if type(obj) != type(np.array([])):
        if obj != 0:
            print(sp.latex(sp.simplify(entry)))
    else:
        for n, entry in enumerate(obj):
            if type(entry) != type(np.array([])) and entry != 0:
                    print(str(position + [n]) + ": ")
                    print(sp.latex(sp.simplify(entry)))
            else:
                lprint(entry, position + [n])

if __name__ == "__main__":
    t = sp.Symbol('t')
    r = sp.Symbol('r')
    theta = sp.Symbol('theta')
    phi = sp.Symbol('phi')
    k = sp.Symbol('k')
    a = sp.Function('a')(t)
    b = sp.Function('b')(t)
    c = sp.Function('c')(t)
    M = sp.Symbol('M')
    factor = 1 - (2*M)/r

    w = sp.Symbol('w')
    rho = sp.Symbol('rho')
    p = w*rho

    x = sp.Symbol('x')
    y = sp.Symbol('y')
    z = sp.Symbol('z')

    #metric = np.diag([-factor, 1/factor, r**2, r**2*sp.sin(theta)**2])
    #metric = np.diag([-1, a**2/(1-k*r**2), a**2*r**2,a**2*r**2*sp.sin(theta)**2])
    metric = np.diag([-1, a**2, b**2, c**2])
    metric_key = [t, x, y, z]
    #metric_key = [t, r, theta, phi] #In order, which variable each row/column of the metric represents

    einstein = raise_one_index(einstein_tensor_from_scratch(metric, metric_key), metric)
    rprint(einstein)
    #sp.pprint(einstein_equations(einstein, np.diag([-rho, p, p, p])))

    #c_syms = christoffel_symbols(metric, metric_key)
    #reimann_t = reimann_tensor(c_syms, metric_key)
    #rprint(lower_one_index(reimann_t, metric))


