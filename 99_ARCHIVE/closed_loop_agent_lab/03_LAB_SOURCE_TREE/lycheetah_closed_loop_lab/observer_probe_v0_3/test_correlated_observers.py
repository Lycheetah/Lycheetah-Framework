import unittest
from correlated_observers import joint_miss_probability, build_grid

class CorrelatedObserverTests(unittest.TestCase):
    def test_independence_gives_product_of_marginals(self):
        self.assertAlmostEqual(joint_miss_probability(.1, 0), .01)

    def test_perfect_common_mode_gives_single_observer_miss_rate(self):
        self.assertAlmostEqual(joint_miss_probability(.1, 1), .1)

    def test_more_positive_correlation_does_not_improve_joint_miss(self):
        values = [joint_miss_probability(.1, rho) for rho in (0, .25, .5, .75, 1)]
        self.assertEqual(values, sorted(values))

    def test_invalid_parameters_rejected(self):
        for p, rho in ((-0.1, 0), (1.1, 0), (.1, -0.1), (.1, 1.1)):
            with self.subTest(p=p, rho=rho):
                with self.assertRaises(ValueError):
                    joint_miss_probability(p, rho)

    def test_grid_has_15_combinations(self):
        self.assertEqual(len(build_grid()), 15)

if __name__ == "__main__":
    unittest.main()
