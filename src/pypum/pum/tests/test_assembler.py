from __future__ import division

from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve, bicg
#from scipy.sparse.linalg.dsolve import linsolve
from numpy.linalg import solve
import numpy as np

from pypum.apps.discretisation import ReactionDiffusion
from pypum.pum.assembler import Assembler
from pypum.pum.dofmanager import DofManager
from pypum.pum.monomialbasis import MonomialBasis
from pypum.pum.basis import BasisSet
from pypum.pum.pu_cy import PU
from pypum.pum.tensorquadrature import TensorQuadrature
from pypum.pum.pufunction_cy import PUFunction
from pypum.utils.box import Box
from pypum.utils.ntree import nTree
from pypum.utils.plotter import Plotter
from pypum.utils.testing import *

import logging
logger = logging.getLogger(__name__)

# setup logging
# log level and format configuration
LOG_LEVEL = logging.DEBUG
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=__file__[:-2] + 'log', level=LOG_LEVEL,
                    format=log_format)

# patch scaling
scaling = 1.25
# set initial cover refinements
refines = 1
# set maximal polynomial degree of patch basis
maxdegree = 1
# plotting flags
plot_patches = True
plot_solution = False

def xtest_mv():
    import numpy as np
    from pypum.pum.monomialbasis_cy import test_mv
    ty = np.ndarray([10])
    y = test_mv(ty)
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print y.shape
    print [y for y in y]
    print "ty", ty.shape, ty
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

def test_assembler1d():
    # setup discretisation
    # --------------------
    # setup PU
    bbox = Box([[0, 1]])
    tree = nTree(bbox=bbox)
    tree.refine(refines)
    pu = PU(tree, weighttype='bspline3', scaling=scaling)
    
    # setup monomial basis
    basis = MonomialBasis(maxdegree, 1)
    basisset = BasisSet(basis)
    # setup dof manager
    ids = [id for id in tree.leafs()]
    dof = DofManager(ids, basisset)
    # setup quadrature
    quad = TensorQuadrature()
    # setup assembler
    asm = Assembler(tree, pu, basisset, dof, quad)
    
    # assemble problem
    # ----------------
    N = dof.dim()
    logger.info("system has dimension " + str(N))
    A = lil_matrix((N, N))
    b = np.zeros(N)
    PDE = ReactionDiffusion(basedegree=maxdegree, D=1, r=1)
    asm.assemble(A, b, lhs=PDE.lhs, rhs=PDE.rhs, symmetric=True)

    # solve system
    # ------------
    A = A.tocsr()
    x = spsolve(A, b)
#    x = bicg(A, b)

    print A.todense()
    print b
    print x
    print x.shape
    
    # plot solution
    if plot_solution:
        puf = PUFunction(x, tree, pu, basisset, dof)
        Plotter.plot(lambda x: puf(x, gradient=False), 1, [0, 1], resolution=1 / 3, vectorized=False)


def xtest_assembler2d():
    # setup discretisation
    # --------------------
    # setup PU
    bbox = Box([[0, 1], [0, 1]])
    tree = nTree(bbox=bbox)
#    tree.refine(refines)
    tree.refine(refines)
    pu = PU(tree, weighttype='bspline3', scaling=scaling)
    if plot_patches:
        pu.tree.plot2d()
    # setup monomial basis
    basis = MonomialBasis(maxdegree, 2)
    basisset = BasisSet(basis)
    # setup dof manager
    ids = [id for id in tree.leafs()]
    dof = DofManager(ids, basisset)
    # setup quadrature
    quad = TensorQuadrature()
    # setup assembler
    asm = Assembler(tree, pu, basisset, dof, quad)
    
    # assemble problem
    # ----------------
    N = dof.dim()
    logger.info("system has dimension " + str(N))
    print "PROBLEM SIZE %i" % N
    A = lil_matrix((N, N))
    b = np.zeros(N)
    PDE = ReactionDiffusion(basedegree=maxdegree, D=1, r=1)
    asm.assemble(A, b, lhs=PDE.lhs, rhs=PDE.rhs, symmetric=True)

    # solve system
    # ------------
    A = A.tocsr()
    x = spsolve(A, b)
#    x = bicg(A, b)

#    print A.todense()
#    print b
#    print x
#    print x.shape
    
    # plot solution
    if plot_solution:
        puf = PUFunction(x, tree, pu, basisset, dof)
        Plotter.plot(lambda x: puf(x, gradient=False), 2, [[0, 1], [0, 1]], resolution=1 / 3, vectorized=False)

test_main()
