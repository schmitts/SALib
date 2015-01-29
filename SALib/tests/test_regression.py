from __future__ import division
from numpy.testing import assert_allclose
from nose.tools import with_setup
from .test_util import teardown
import numpy as np
import sys

from ..sample.morris import sample
from ..analyze import morris
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.sample import fast_sampler
from SALib.analyze import fast
from SALib.sample import finite_diff
from SALib.analyze import dgsm
from SALib.sample import latin
from SALib.analyze import delta
from ..test_functions import Ishigami
from ..util import read_param_file


def test_regression_morris_vanilla():

    param_file ='SALib/test_functions/params/Ishigami.txt'
    problem = read_param_file(param_file)
    param_values = sample(problem=problem, N=5000, \
                          num_levels=10, grid_jump=5, \
                          optimal_trajectories=None)

    np.savetxt('model_input.txt', param_values, delimiter=' ')

    Y = Ishigami.evaluate(param_values)
    np.savetxt("model_output.txt", Y, delimiter=' ')

    Si = morris.analyze(param_file, 'model_input.txt', 'model_output.txt',
                        column=0, conf_level=0.95, print_to_console=False,
                        num_levels=10, grid_jump=5)

    assert_allclose(Si['mu_star'], [8.1, 2.2, 5.4], atol=0, rtol=5e-1)


def test_regression_morris_groups():

    param_file = 'SALib/test_functions/params/Ishigami_groups.txt'
    problem = read_param_file(param_file)

    param_values = sample(problem=problem, N=5000, \
                          num_levels=10, grid_jump=5, \
                          optimal_trajectories=None)

    np.savetxt('model_input_groups.txt', param_values, delimiter=' ')

    Y = Ishigami.evaluate(param_values)
    np.savetxt("model_output_groups.txt", Y, delimiter=' ')

    Si = morris.analyze(param_file, 'model_input_groups.txt', 'model_output_groups.txt',
                        column=0, conf_level=0.95, print_to_console=False,
                        num_levels=10, grid_jump=5)

    assert_allclose(Si['mu_star'], [7.87, 6.26], rtol=5e-1)


def test_regression_morris_optimal():
    '''
    Tests the use of optimal trajectories with Morris.

    Note that the relative tolerance is set to a very high value (default is 1e-05)
    due to the coarse nature of the num_levels and grid_jump.
    '''
    param_file = 'SALib/test_functions/params/Ishigami.txt'
    problem = read_param_file(param_file)
    param_values = sample(problem=problem, N=20, \
                          num_levels=4, grid_jump=2, \
                          optimal_trajectories=9)

    np.savetxt('model_input_groups.txt', param_values, delimiter=' ')

    Y = Ishigami.evaluate(param_values)

    np.savetxt("model_output_groups.txt", Y, delimiter=' ')

    Si = morris.analyze(param_file, 'model_input_groups.txt', 'model_output_groups.txt',
                        column=0, conf_level=0.95, print_to_console=False,
                        num_levels=4, grid_jump=2)

    assert_allclose(Si['mu_star'], [8.1, 2.2, 5.4], rtol=10)


def test_regression_sobol():
    param_file = 'SALib/test_functions/params/Ishigami.txt'
    param_values = saltelli.sample(10000, param_file, calc_second_order=True)

    Y = Ishigami.evaluate(param_values)
    np.savetxt('model_output.txt', Y, delimiter=' ')

    Si = sobol.analyze(param_file, 'model_output.txt', column=0,
                       calc_second_order=True, conf_level=0.95, print_to_console=False)

    assert_allclose(Si['S1'], [0.31, 0.44, 0.00], atol=5e-2, rtol=1e-1)
    assert_allclose(Si['ST'], [0.55, 0.44, 0.24], atol=5e-2, rtol=1e-1)
    assert_allclose([Si['S2'][0][1], Si['S2'][0][2], Si['S2'][1][2]], [0.00, 0.25, 0.00], atol=5e-2, rtol=1e-1)


def test_regression_fast():
    param_file = 'SALib/test_functions/params/Ishigami.txt'
    param_values = fast_sampler.sample(1000, param_file)

    Y = Ishigami.evaluate(param_values)
    np.savetxt("model_output.txt", Y, delimiter=' ')

    Si = fast.analyze(param_file, 'model_output.txt', column=0, print_to_console=False)
    assert_allclose(Si['S1'], [0.31, 0.44, 0.00], atol=5e-2, rtol=1e-1)
    assert_allclose(Si['ST'], [0.55, 0.44, 0.24], atol=5e-2, rtol=1e-1)


def test_regression_dgsm():
    param_file = 'SALib/test_functions/params/Ishigami.txt'
    param_values = finite_diff.sample(10000, param_file, delta=0.001)

    np.savetxt('model_input.txt', param_values, delimiter=' ')
    Y = Ishigami.evaluate(param_values)
    np.savetxt('model_output.txt', Y, delimiter=' ')

    Si = dgsm.analyze(param_file, 'model_input.txt', 'model_output.txt',
                      column=0, conf_level=0.95, print_to_console=False)

    assert_allclose(Si['dgsm'], [2.229, 7.066, 3.180], atol=5e-2, rtol=1e-1)


def test_regression_delta():
    param_file = 'SALib/test_functions/params/Ishigami.txt'
    param_values = latin.sample(10000, param_file)

    np.savetxt('model_input.txt', param_values, delimiter=' ')
    Y = Ishigami.evaluate(param_values)
    np.savetxt('model_output.txt', Y, delimiter=' ')

    Si = delta.analyze(param_file, 'model_input.txt', 'model_output.txt',
                   column=0, num_resamples=10, conf_level=0.95, print_to_console=True)

    assert_allclose(Si['delta'], [0.210, 0.358, 0.155], atol=5e-2, rtol=1e-1)
    assert_allclose(Si['S1'], [0.31, 0.44, 0.00], atol=5e-2, rtol=1e-1)
