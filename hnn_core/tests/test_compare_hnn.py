import os.path as op

from numpy import loadtxt
from numpy.testing import assert_array_equal

from mne.utils import _fetch_file
import hnn_core
from hnn_core import simulate_dipole, read_params, Network


def test_hnn_core():
    """Test to check if MNE neuron does not break."""
    # small snippet of data on data branch for now. To be deleted
    # later. Data branch should have only commit so it does not
    # pollute the history.
    data_url = ('https://raw.githubusercontent.com/jonescompneurolab/'
                'hnn-core/test_data/dpl.txt')
    if not op.exists('dpl.txt'):
        _fetch_file(data_url, 'dpl.txt')
    dpl_master = loadtxt('dpl.txt')

    hnn_core_root = op.join(op.dirname(hnn_core.__file__), '..')

    params_fname = op.join(hnn_core_root, 'param', 'default.json')
    params = read_params(params_fname)

    net = Network(params, n_jobs=1)
    dpl = simulate_dipole(net)[0]

    fname = './dpl2.txt'
    dpl.write(fname)

    dpl_pr = loadtxt(fname)
    assert_array_equal(dpl_pr[:, 2], dpl_master[:, 2])  # L2
    assert_array_equal(dpl_pr[:, 3], dpl_master[:, 3])  # L5

    # Test spike type counts
    spiketype_counts = {}
    for spikegid in net.spikegids[0]:
        if net.gid_to_type(spikegid) not in spiketype_counts:
            spiketype_counts[net.gid_to_type(spikegid)] = 0
        else:
            spiketype_counts[net.gid_to_type(spikegid)] += 1
    assert 'extinput' not in spiketype_counts
    assert 'exgauss' not in spiketype_counts
    assert 'extpois' not in spiketype_counts
    assert spiketype_counts == {'evprox1': 269,
                                'L2_basket': 54,
                                'L2_pyramidal': 113,
                                'L5_pyramidal': 395,
                                'L5_basket': 85,
                                'evdist1': 234,
                                'evprox2': 269}
