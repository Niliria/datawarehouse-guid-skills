import sys
import tempfile
import unittest
from pathlib import Path
import re

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from main import CDMModelingSkill  # noqa: E402
from parse_upstream_outputs import UpstreamOutputParser  # noqa: E402


class UpstreamContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        upstream_dir = REPO_ROOT / "output" / "dwm-bus-matrix"
        cls.input_paths = {
            "business_process_file": upstream_dir / "dwm_bp_business_process.csv",
            "subject_area_file": upstream_dir / "dwm_bp_subject_area.csv",
            "dim_spec_file": upstream_dir / "dwm_dim_spec.csv",
            "dwd_fact_spec_file": upstream_dir / "dwm_dwd_fact_spec.csv",
            "bus_matrix_file": upstream_dir / "dwm_bus_matrix.xlsx",
            "dim_join_spec_file": upstream_dir / "dwm_dim_join_spec.csv",
            "dwd_join_spec_file": upstream_dir / "dwm_dwd_join_spec.csv",
        }
        parser = UpstreamOutputParser(
            **{key: str(value) for key, value in cls.input_paths.items()},
            base_dir=REPO_ROOT,
        )
        cls.model = parser.parse()

    def test_latest_upstream_files_are_fully_parsed(self):
        self.assertEqual(4, len(self.model["dimensions"]))
        self.assertEqual(6, len(self.model["processes"]))
        self.assertEqual(6, len(self.model["matrix_links"]) // 2)

        dimensions = {item["table_name"]: item for item in self.model["dimensions"]}
        self.assertEqual("user_id", dimensions["dim_user"]["business_key"])
        self.assertEqual("BIGINT", dimensions["dim_user"]["business_key_type"])
        self.assertEqual(2, dimensions["dim_user"]["scd_type"])
        self.assertEqual("user_info", dimensions["dim_user"]["source_joins"][0]["source_table"])

    def test_skill_markdown_is_consolidated_to_five_files(self):
        markdown_files = [SKILL_ROOT / "SKILL.md", *sorted((SKILL_ROOT / "references").glob("*.md"))]
        self.assertEqual(5, len(markdown_files))

        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        references = set(re.findall(r"`(references/[^`]+\.md)`", skill_text))
        self.assertEqual(
            {
                "references/upstream-contract.md",
                "references/dim-modeling.md",
                "references/dwd-modeling.md",
                "references/validation.md",
            },
            references,
        )
        for reference in references:
            self.assertTrue((SKILL_ROOT / reference).exists(), reference)

    def test_bus_matrix_resolves_dwd_foreign_keys(self):
        processes = {item["table_name"]: item for item in self.model["processes"]}
        order = processes["dwd_trd_place_order_df"]

        self.assertEqual(["order_id"], order["grain_keys"])
        self.assertEqual({"dim_user", "dim_shop"}, {item["table_name"] for item in order["dimension_refs"]})
        self.assertEqual({"user_id", "shop_id"}, {item["source_field"] for item in order["dimension_refs"]})
        self.assertEqual(3, len(order["measures"]))
        self.assertEqual({"order_time", "pay_time"}, {item["name"] for item in order["detail_fields"]})

    def test_full_generation_uses_latest_upstream_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "cdm-output"
            config_file = temp_path / "skill_config.yaml"
            config = {
                "input": {key: str(value) for key, value in self.input_paths.items()},
                "output": {"target_dir": str(output_dir)},
                "modeling": {
                    "default_scd_type": 1,
                    "default_fact_type": "transaction",
                    "generate_ddl": True,
                    "generate_etl": True,
                },
            }
            config_file.write_text(yaml.safe_dump(config, allow_unicode=True), encoding="utf-8")

            self.assertTrue(CDMModelingSkill(config_file).run())
            self.assertEqual(4, len(list((output_dir / "ddl" / "dim").glob("*.sql"))))
            self.assertEqual(6, len(list((output_dir / "ddl" / "dwd").glob("*.sql"))))
            self.assertEqual(4, len(list((output_dir / "etl" / "dim").glob("*.sql"))))
            self.assertEqual(6, len(list((output_dir / "etl" / "dwd").glob("*.sql"))))

            dim_ddl = (output_dir / "ddl" / "dim" / "dim_user_scd2.sql").read_text(encoding="utf-8")
            self.assertIn("user_id BIGINT", dim_ddl)
            self.assertIn("begin_date STRING", dim_ddl)

            dwd_ddl = (output_dir / "ddl" / "dwd" / "dwd_trd_place_order_df.sql").read_text(encoding="utf-8")
            self.assertIn("order_id BIGINT", dwd_ddl)
            self.assertIn("order_time STRING", dwd_ddl)
            self.assertIn("user_sk BIGINT", dwd_ddl)
            self.assertIn("shop_sk BIGINT", dwd_ddl)

            dwd_etl = (output_dir / "etl" / "dwd" / "load_dwd_trd_place_order_df.sql").read_text(encoding="utf-8")
            self.assertIn("LEFT JOIN dim_user", dwd_etl)
            self.assertIn("source.user_id = dim_user.user_id", dwd_etl)
            self.assertIn("source.order_time AS order_time", dwd_etl)

            report = (output_dir / "docs" / "validation_report.md").read_text(encoding="utf-8")
            self.assertIn("业务过程缺少度量: coupon_use", report)


if __name__ == "__main__":
    unittest.main()
