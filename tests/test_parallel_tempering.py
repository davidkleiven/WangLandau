import unittest
import os
try:
    from ase.ce import BulkCrystal
    from cemc.mcmc import ParallelTempering
    from cemc.mcmc import Montecarlo
    from helper_functions import get_example_ecis
    from cemc import CE
    available = True
    import_msg = ""
except ImportError as exc:
    import_msg = str(exc)
    available = False

db_name = "parallel_tempering.db"


class TestParallelTempering(unittest.TestCase):
    def init_bulk_crystal(self):
        conc_args = {
            "conc_ratio_min_1": [[2, 1, 1]],
            "conc_ratio_max_1": [[0, 2, 2]],
        }
        ceBulk = BulkCrystal(crystalstructure="fcc", a=4.05, size=[4, 4, 4],
                             basis_elements=[["Al", "Mg", "Si"]],
                             conc_args=conc_args, db_name=db_name,
                             max_cluster_size=2, max_cluster_dia=4.0)
        ceBulk.reconfigure_settings()
        ecis = get_example_ecis(bc=ceBulk)
        calc = CE(ceBulk, ecis)
        ceBulk.atoms.set_calculator(calc)
        return ceBulk

    def test_no_throw(self):
        if not available:
            self.skipTest(import_msg)

        ceBulk = self.init_bulk_crystal()
        mc = Montecarlo(ceBulk.atoms, 1000.0)
        # par_temp = ParallelTempering(mc_obj=mc, Tmax=1000.0, Tmin=100.0)


if __name__ == "__main__":
    from cemc import TimeLoggingTestRunner
    unittest.main(testRunner=TimeLoggingTestRunner)
