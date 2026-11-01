
import unittest
import sqlite3
import tempfile
from pathlib import Path
from contextlib import closing

from src.esco.match_esco import classify_match, find_exact_match, save_esco_mapping, save_esco_check
from unittest.mock import patch

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
            classify_match(
                "Python",
                "Python (computer programming)"
            ),
            "review"
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

    
    def test_exact_match_by_alternative_label(self):
        status = classify_match(
            "Python",
            "Python (computer programming)",
            ["Python 3K", "Python"]
        )
        assert status == "exact"


    def test_docker_requires_review(self):
        status = classify_match(
            "Docker",
            "manage ICT virtualisation environments",
            [
                "manage ICT virtualization machines",
                "manage containerization"
            ]
        )
        assert status == "review"


    def test_rpa_requires_review(self):
        status = classify_match(
            "Robotic Process Automation",
            "robotics",
            ["robotic engineering", "mechatronics"]
        )
        assert status == "review"

    @patch("src.esco.match_esco.get_esco_skill_details")
    def test_find_exact_match(self, mock_details):
        results = [
            {"uri": "esco:test-1"},
            {"uri": "esco:test-2"}
        ]

        mock_details.side_effect = [
            {
                "preferredLabel": {"en": "JavaScript"},
                "alternativeLabel": {"en": []}
            },
            {
                "preferredLabel": {"en": "Python (computer programming)"},
                "alternativeLabel": {"en": ["Python"]}
            }
        ]

        result = find_exact_match("Python", results)

        self.assertEqual(result["uri"], "esco:test-2")
        self.assertEqual(result["status"], "exact")
        self.assertEqual(mock_details.call_count, 2)

    @patch("src.esco.match_esco.get_esco_skill_details")
    def test_find_exact_match_not_found(self, mock_details):
        results = [
            {"uri": "esco:test-1"},
            {"uri": "esco:test-2"}
        ]

        mock_details.side_effect = [
            {
                "preferredLabel": {"en": "JavaScript"},
                "alternativeLabel": {"en": []}
            },
            {
                "preferredLabel": {"en": "JavaScript Framework"},
                "alternativeLabel": {"en": []}
            }
        ]

        result = find_exact_match("Node.js", results)

    def test_save_esco_mapping_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "test.db"

            with closing(sqlite3.connect(test_db)) as conn:
                conn.executescript("""
                    CREATE TABLE skill (
                        skill_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL
                    );

                    CREATE TABLE esco_skill (
                        esco_uri TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        version TEXT,
                        fetched_at TEXT
                    );

                    CREATE TABLE skill_mapping (
                        skill_id INTEGER PRIMARY KEY,
                        esco_uri TEXT,
                        status TEXT,
                        mapping_method TEXT,
                        reviewed_at TEXT
                    );

                    INSERT INTO skill VALUES (1, 'Python');

                    INSERT INTO esco_skill
                        (esco_uri, title)
                    VALUES ('esco:original', 'Python');

                    INSERT INTO skill_mapping
                        (skill_id, esco_uri, status, mapping_method)
                    VALUES (1, 'esco:original', 'exact', 'manual');
                """)

            with patch("src.esco.match_esco.DB_PATH", test_db):
                save_esco_mapping(
                    "Python",
                    "Another Python",
                    "esco:new"
                )

            with closing(sqlite3.connect(test_db)) as conn:
                row = conn.execute("""
                    SELECT esco_uri, status, mapping_method
                    FROM skill_mapping
                    WHERE skill_id = 1
                """).fetchone()

            self.assertEqual(
                row,
                ("esco:original", "exact", "manual")
            )

    
    def test_save_esco_mapping_automatic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "test.db"

            with closing(sqlite3.connect(test_db)) as conn:
                with conn:
                    conn.executescript("""
                        CREATE TABLE skill (
                            skill_id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL
                        );

                        CREATE TABLE esco_skill (
                            esco_uri TEXT PRIMARY KEY,
                            title TEXT NOT NULL,
                            version TEXT,
                            fetched_at TEXT
                        );

                        CREATE TABLE skill_mapping (
                            skill_id INTEGER PRIMARY KEY,
                            esco_uri TEXT,
                            status TEXT,
                            mapping_method TEXT,
                            reviewed_at TEXT
                        );

                        INSERT INTO skill VALUES (1, 'JavaScript');
                    """)

            with patch("src.esco.match_esco.DB_PATH", test_db):
                save_esco_mapping(
                    "JavaScript",
                    "JavaScript",
                    "esco:javascript",
                    mapping_method="automatic"
                )

            with closing(sqlite3.connect(test_db)) as conn:
                row = conn.execute("""
                    SELECT esco_uri, status, mapping_method
                    FROM skill_mapping
                    WHERE skill_id = 1
                """).fetchone()

            self.assertEqual(
                row,
                ("esco:javascript", "exact", "automatic")
            )

    def test_save_esco_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "test.db"

            with closing(sqlite3.connect(test_db)) as conn:
                with conn:
                    conn.executescript("""
                        CREATE TABLE skill (
                            skill_id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL
                        );

                        CREATE TABLE esco_check (
                            skill_id INTEGER PRIMARY KEY,
                            status TEXT NOT NULL,
                            checked_at TEXT NOT NULL,
                            esco_version TEXT NOT NULL
                        );

                        INSERT INTO skill VALUES (1, 'Node.js');
                    """)

            with patch("src.esco.match_esco.DB_PATH", test_db):
                save_esco_check("Node.js", "no_match")

            with closing(sqlite3.connect(test_db)) as conn:
                row = conn.execute("""
                    SELECT status, esco_version, checked_at
                    FROM esco_check
                    WHERE skill_id = 1
                """).fetchone()

            self.assertEqual(row[0], "no_match")
            self.assertEqual(row[1], "v1.2.0")
            self.assertTrue(row[2])



if __name__ == "__main__":
    unittest.main()
