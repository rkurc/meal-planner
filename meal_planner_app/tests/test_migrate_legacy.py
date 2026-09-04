"""Tests for relational CSV extract used by legacy migration."""

import csv
import os
import tempfile
import unittest

from meal_planner_app.migrate_legacy import extract_from_csvs


def _write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class TestExtractFromCsvs(unittest.TestCase):
    """extract_from_csvs must produce API-valid recipes."""

    def test_empty_instructions_get_placeholder(self):
        """A blank przepis field still yields non-empty instructions."""
        with tempfile.TemporaryDirectory() as tmp:
            _write_csv(
                os.path.join(tmp, "przepisy.csv"),
                ["id", "nazwa", "przepis", "liczbaPorcji"],
                [
                    {
                        "id": "71",
                        "nazwa": "placki z kasza kuskus",
                        "przepis": "",
                        "liczbaPorcji": "2",
                    }
                ],
            )
            _write_csv(
                os.path.join(tmp, "produkty.csv"),
                ["id", "nazwa", "idJednostki", "idLokalizacji"],
                [
                    {
                        "id": "1",
                        "nazwa": "kuskus",
                        "idJednostki": "0",
                        "idLokalizacji": "",
                    }
                ],
            )
            _write_csv(
                os.path.join(tmp, "skladniki.csv"),
                ["idPrzepisu", "idProduktu", "liczba"],
                [{"idPrzepisu": "71", "idProduktu": "1", "liczba": "100"}],
            )
            _write_csv(
                os.path.join(tmp, "jednostki.csv"),
                ["idJednostki", "nazwa"],
                [{"idJednostki": "0", "nazwa": "g"}],
            )

            recipes = extract_from_csvs(tmp)

        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0]["name"], "placki z kasza kuskus")
        self.assertTrue(recipes[0]["instructions"].strip())
        self.assertEqual(recipes[0]["ingredients"][0]["name"], "kuskus")
        self.assertEqual(recipes[0]["ingredients"][0]["quantity"], "100")
        self.assertEqual(recipes[0]["ingredients"][0]["unit"], "g")
