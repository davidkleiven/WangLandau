import sys
from wanglandau.ce_calculator import CE
from ase.build import bulk
from ase.ce.settings import BulkCrystal
from wanglandau.sa_sgc import SimmualtedAnnealingSGC
from ase.visualize import view
from matplotlib import pyplot as plt
from mcmc import montecarlo as mc
from mcmc import mc_observers as mc_obs
from ase.units import kB
import numpy as np
import json

# Hard coded ECIs obtained from the ce_hydrostatic.db runs
ecis = {'c3_1225_4_1': -0.00028826723864655595,
        'c2_1000_1_1': -0.012304759727020153,
        'c4_1225_7_1': 0.00018000893943061064,
        'c2_707_1_1': 0.01078731693580544,
        'c4_1225_3_1': 0.00085623111812932343,
        'c2_1225_1_1': -0.010814400169849577,
        'c1_1': -1.0666948263880078,
        'c4_1000_1_1': 0.0016577886586285448,
        'c4_1225_2_1': 0.01124654696678576,
        'c3_1225_2_1': -0.017523737495758165,
        'c4_1225_6_1': 0.0038879587131474451,
        'c4_1225_5_1': 0.00060830459771275532,
        'c3_1225_3_1': -0.011318935831421125,
        u'c0': -2.6466290360293874}

ecis = {'c3_1225_4_1': -0.00028826723864655595,
        'c2_1000_1_1': -0.012304759727020153,
        'c4_1225_7_1': 0.00018000893943061064,
        'c2_707_1_1': 0.01078731693580544,
        'c4_1225_3_1': 0.00085623111812932343,
        'c2_1225_1_1': -0.010814400169849577,
        'c4_1000_1_1': 0.0016577886586285448,
        'c4_1225_2_1': 0.01124654696678576,
        'c3_1225_2_1': -0.017523737495758165,
        'c4_1225_6_1': 0.0038879587131474451,
        'c4_1225_5_1': 0.00060830459771275532,
        'c3_1225_3_1': -0.011318935831421125}

def mcmc( ceBulk, c_mg ):
    n_mg = int( c_mg*len(ceBulk.atoms) )
    for i in range(n_mg):
        ceBulk.atoms._calc.update_cf( (i,"Al","Mg") )
    ceBulk.atoms._calc.clear_history()
    formula = ceBulk.atoms.get_chemical_formula()
    out_file = "data/pair_corrfuncs_tempdependent%s.json"%(formula)
    temps = [250]
    n_burn = 40000
    n_sampling = 500000
    cfs = []
    cf_std = []
    n_samples = []
    orig_nn = ecis["c2_707_1_1"]
    energy = []
    heat_cap = []
    for T in temps:
        print ("Current temperature {}K".format(T))
        ecis["c2_707_1_1"] = orig_nn - 0.12*kB*T
        ceBulk.atoms._calc.update_ecis(ecis)
        mc_obj = mc.Montecarlo( ceBulk.atoms, T )
        mc_obj.runMC( steps=n_burn, verbose=False )

        # Run Monte Carlo
        obs = mc_obs.PairCorrelationObserver( ceBulk.atoms._calc )
        mc_obj.attach( obs, interval=1 )
        mc_obj.runMC( steps=n_sampling )
        cfs.append( obs.get_average() )
        cf_std.append( obs.get_std() )
        n_samples.append( obs.n_entries )
        thermo = mc_obj.get_thermodynamic()
        energy.append( thermo["energy"] )
        heat_cap.append( thermo["heat_capacity"] )

    try:
        with open( out_file, 'r') as infile:
            data = json.load(infile)
    except:
        data = {}
        data["temperature"] = []
        data["cfs"] = []
        data["cf_std"] = []
        data["n_samples"] = []
        data["energy"] = []
        data["heat_capacity"] = []

    data["temperature"] += temps
    data["cfs"] += cfs
    data["cf_std"] += cf_std
    data["n_samples"] += n_samples
    data["energy"] += energy
    data["heat_capacity"] += heat_cap
    with open( out_file, 'w') as outfile:
        json.dump( data, outfile )

def main( run ):
    atoms = bulk("Al")
    atoms = atoms*(4,4,4)
    atoms[0].symbol = "Mg"

    db_name = "/home/davidkl/Documents/WangLandau/data/ce_hydrostatic_7x7.db"
    conc_args = {
        "conc_ratio_min_1":[[60,4]],
        "conc_ratio_max_1":[[64,0]],
    }
    ceBulk = BulkCrystal( "fcc", 4.05, [20,20,20], 1, [["Al","Mg"]], conc_args, db_name, max_cluster_size=4, max_cluster_dia=1.414*4.05,reconf_db=False)
    init_cf = {key:1.0 for key in ecis.keys()}

    calc = CE( ceBulk, ecis, initial_cf=init_cf )
    ceBulk.atoms.set_calculator( calc )

    if ( run == "MC" ):
        mcmc( ceBulk, 0.1 )
    else:
        chem_pot = {
        "Al":0.0,
        "Mg":0.0
        }
        gs_finder = SimmualtedAnnealingSGC( ceBulk.atoms, chem_pot, "test_db.db" )
        gs_finder.run( n_steps=1000, Tmin=400, ntemps=10 )
        gs_finder.show_visit_stat()
        gs_finder.show_compositions()
    view( ceBulk.atoms )
    #plt.show()

if __name__ == "__main__":
    #run = sys.argv[1] # Run is WL or MC
    run = "MC"
    main( run )