from __future__ import division
import numpy as np

class ReactionDiffusion(object):
    """Discretisation of the second order elliptic reaction-diffusion problem
        -D \Laplace u + ru = f
    """
    def __init__(self, D, r, f=lambda _:1):
        self._D = D
        self._r = r
        self._f = f

    def lhs(self, A, idx1, idx2, basis1, basis2, quad, intbox, boundary):
        # NOTE: the quadrature degree should depend on the weight function, the basis degree, coefficients and the equation 
        basisdim1 = len(basis1)
        basisdim2 = len(basis2)
        D = self._D
        r = self._r
        tx, w = quad.transformed(intbox, basisdim1)
        for j, bj in zip(range(idx1, idx1 + basisdim1), basis1):    
            for k, bk in zip(range(idx2, idx2 + basisdim2), basis2):
                # operator matrix with diffusion and reaction
                print "AAA-0", tx
                print "AAA-1", bj.dx(tx)
                print "AAA-2", bj(tx)
                print "AAA-3", np.inner(bj.dx(tx), bk.dx(tx))
                val = D * np.inner(bj.dx(tx), bk.dx(tx)) + r * bj(tx) * bk(tx)
                A[j, k] = sum(w * val)
    
    def rhs(self, b, idx2, basis2, quad, intbox, boundary):
        basisdim2 = len(basis2)
        tx, w = quad.transformed(intbox, basisdim2)
        for k, bk in zip(range(idx2, idx2 + basisdim2), basis2):
            # source term
            val = f(tx) * bk(tx)
            b[k] = sum(w * val) 
            # treat boundary
            for bndbox, normal in boundary:
                txb, wb = quad.transformed(bndbox, basisdim2)
                # TODO
