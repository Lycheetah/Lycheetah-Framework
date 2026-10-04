import unittest
from validator import validate

class NamingForgeV02Tests(unittest.TestCase):
    def test_bundle(self):
        errors, warnings = validate()
        self.assertEqual(errors, [])

if __name__ == "__main__":
    unittest.main()
