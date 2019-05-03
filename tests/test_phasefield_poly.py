import unittest
try:
    from phasefield_cxx import PyPolynomialTerm, PyPolynomial
    reason = ""
    available = True
except ImportError as exc:
    available = False
    reason = str(exc)


class TestPhaseFieldPolynomial(unittest.TestCase):
    def test_phase_field_poly(self):
        if not available:
            self.skipTest(reason)
        term1 = PyPolynomialTerm([2, 3])
        term2 = PyPolynomialTerm([1, 2])

        poly = PyPolynomial(2)
        poly.add_term(1.0, term1)
        poly.add_term(-2.0, term2)
        self.assertAlmostEqual(poly.evaluate([-1.0, 3.0]), 45.0)
        self.assertAlmostEqual(poly.deriv([-1.0, 3.0], 0), -72.0)
        self.assertAlmostEqual(poly.deriv([-1.0, 3.0], 1), 39.0)

if __name__ == "__main__":
    from cemc import TimeLoggingTestRunner
    unittest.main(testRunner=TimeLoggingTestRunner)