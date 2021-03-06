import unittest
import numpy as np
try:
    from cemc.tools import TwoPhaseLandauPolynomial
    available = True
    reason = ""
except ImportError as exc:
    available = False
    reason = str(exc)
    print(str(exc))

class TestLandauPolynomial(unittest.TestCase):

    def test_fit(self):
        if not available:
            self.skipTest(reason)
        error = False
        msg = ""
        try:
            conc1 = np.linspace(0.0, 0.3, 100)
            F1 = conc1**2
            conc2 = np.linspace(0.6, 1.0, 100)
            F2 = 0.5*(conc2-0.9)**2
            poly = TwoPhaseLandauPolynomial(c1=0.0, c2=0.5)
            poly.fit(conc1, F1, conc2, F2)
            # show_fit(poly, conc1, conc2, F1, F2)
        except Exception as exc:
            error = True
            msg = str(exc)

        self.assertFalse(error, msg=msg)

def show_fit(poly, conc1, conc2, F1, F2):
    import matplotlib as mpl
    mpl.rcParams.update({"svg.fonttype": "none",
                         "font.size": 18,
                         "axes.unicode_minus": False})

    from matplotlib import pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(conc1, F1, "x")
    ax.plot(conc2, F2, "o", mfc="none")
    c = np.linspace(np.min(conc1), np.max(conc2), 100)
    fitted = [poly.eval_at_equil(c[i]) for i in range(len(c))]
    ax.plot(c, fitted)

    ax2 = ax.twinx()
    n_eq = [poly.equil_shape_order(c[i]) for i in range(len(c))]
    ax2.plot(c, n_eq)
    ax.set_xlabel("Concentration")
    ax.set_ylabel("Free energy")
    ax2.set_ylabel("Long range order parameter")
    plt.show()




if __name__ == "__main__":
    from cemc import TimeLoggingTestRunner
    unittest.main(testRunner=TimeLoggingTestRunner)
