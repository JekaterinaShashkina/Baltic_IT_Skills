
import unittest

from src.match_esco import classify_match


class TestEscoMatching(unittest.TestCase):

    def test_identical_names(self):
        self.assertEqual(
            classify_match("Java", "Java"),
            "exact"
        )

    def test_case_insensitive(self):
        self.assertEqual(
            classify_match("python", "PYTHON"),
            "exact"
        )

    def test_parentheses(self):
        self.assertEqual(
            classify_match("Python", "Python (computer programming)"),
            "exact"
        )

    def test_different_concepts(self):
        self.assertEqual(
            classify_match("Robotic Process Automation", "robotics"),
            "review"
        )

    def test_combined_languages(self):
        self.assertEqual(
            classify_match("C / C++", "C++"),
            "review"
        )

    def test_related_tool(self):
        self.assertEqual(
            classify_match("CI and CD", "Jenkins (tools for software configuration management)"),
            "review"
        )


if __name__ == "__main__":
    unittest.main()
