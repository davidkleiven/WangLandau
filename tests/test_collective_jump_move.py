import unittest
from ase.build import bulk
from ase import Atoms
from ase.spacegroup import get_spacegroup
try:
    from cemc.mcmc import CollectiveJumpMove
    available = True
except Exception as exc:
    print (exc)
    reason = str(exc)
    available = False

class TestCollectiveJump( unittest.TestCase ):
    def test_no_throw(self):
        if (not available):
            self.skipTest(reason)
            return
        no_throw = True
        msg = ""
        try:
            atoms = bulk("Al",cubic=True)

            # Add one site at the center
            L = atoms.get_cell()[0,0]
            at = Atoms( "X", positions=[[L/2,L/2,L/2]] )
            atoms.extend(at)
            sp_gr = get_spacegroup(atoms)

            sc = atoms*(2,2,2)
            jump_moves = CollectiveJumpMove(mc_cell=sc)
        except Exception as exc:
            msg = str(exc)
            no_throw = False
        self.assertTrue(no_throw, msg=msg)

if __name__ == "__main__":
    from cemc import TimeLoggingTestRunner
    unittest.main(testRunner=TimeLoggingTestRunner)
