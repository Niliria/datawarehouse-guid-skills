"""
parse_upstream_outputs.py - 上游产物解析模块
========================================
读取总线矩阵解析文档和 ODS 元数据解析文档，合并为 CDM 生成所需的统一上下文。
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any

import yaml


class UpstreamOutputParser:
    """解析上游总线矩阵文档和 ODS 元数据解析文档。"""

    def __init__(self, bus_matrix_doc: str, ods_metadata_doc: str, base_dir: Path, logger=None):
        self.base_dir = Path(base_dir)
        self.bus_matrix_doc = self._resolve_path(bus_matrix_doc)
        self.ods_metadata_doc = self._resolve_path(ods_metadata_doc)
        self.logger = logger
        self.warnings: List[str] = []

    def parse(self) -> Dict[str, Any]:
        bus_doc = self._load_document(self.bus_matrix_doc)
        ods_doc = self._load_document(self.ods_metadata_doc)

        processes = self._extract_processes(bus_doc)
        ods_tables = self._extract_ods_tables(ods_doc)
        dimensions = self._build_dimensions(processes, ods_tables)

        model = {
            "processes": processes,
            "dimensions": dimensions,
            "ods_tables": ods_tables,
            "warnings": self.warnings,
        }
        self._validate(model)
        return model

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path
        return self.base_dir / path

    def _load_document(self, path: Path) -> Any:
        if not path.exists():
            self._warn(f"输入文档不存在: {path}")
            return {}

        text = path.read_text(encoding="utf-8")
        suffix = path.suffix.lower()

        if suffix == ".json":
            return json.loads(text)
        if suffix in {".yaml", ".yml"}:
            return yaml.safe_load(text) or {}

        fenced = self._load_fenced_structured_block(text)
        if fenced:
            return fenced
        return {"markdown_tables": self._parse_markdown_tables(text), "raw_text": text}

    def _load_fenced_structured_block(self, text: str) -> Any:
        for lang, block in re.findall(r"```(yaml|yml|json)\s+(.*?)```", text, re.DOTALL | re.IGNORECASE):
            if lang.lower() == "json":
                return json.loads(block)
            return yaml.safe_load(block) or {}
        return {}

    def _parse_markdown_tables(self, text: str) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if "|" not in line or idx + 1 >= len(lines):
                continue
            next_line = lines[idx + 1]
            if not re.search(r"\|\s*:?-{3,}:?\s*\|", next_line):
                continue
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            row_idx = idx + 2
            while row_idx < len(lines) and "|" in lines[row_idx]:
                cells = [cell.strip() for cell in lines[row_idx].strip("|").split("|")]
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                row_idx += 1
        return rows

    def _extract_processes(self, doc: Any) -> List[Dict[str, Any]]:
        if isinstance(doc, dict) and "processes" in doc:
            return [self._normalize_process(item) for item in doc.get("processes", [])]

        rows = doc.get("markdown_tables", []) if isinstance(doc, dict) else []
        processes = []
        for row in rows:
            if not self._row_has(row, ["数据域", "业务过程"]):
                continue
            processes.append(self._normalize_process({
                "domain": self._pick(row, ["数据域", "domain"]),
                "business_process": self._pick(row, ["业务过程", "process", "business_process"]),
                "grain": self._pick(row, ["粒度", "grain", "granularity"]),
                "dimensions": self._split_list(self._pick(row, ["一致性维度", "维度", "dimensions"])),
                "measures": self._split_measures(self._pick(row, ["度量", "度量值", "measures"])),
                "source_tables": self._split_list(self._pick(row, ["源表", "source_tables", "来源表"])),
            }))
        return processes

    def _extract_ods_tables(self, doc: Any) -> Dict[str, Dict[str, Any]]:
        tables: Dict[str, Dict[str, Any]] = {}
        raw_tables = doc.get("tables", []) if isinstance(doc, dict) else []
        for table in raw_tables:
            table_name = table.get("table_name") or table.get("name")
            if not table_name:
                continue
            tables[table_name] = {
                "table_name": table_name,
                "domain": table.get("domain", ""),
                "description": table.get("description", ""),
                "fields": [self._normalize_field(field) for field in table.get("fields", [])],
            }

        rows = doc.get("markdown_tables", []) if isinstance(doc, dict) else []
        for row in rows:
            table_name = self._pick(row, ["表名", "table_name", "ODS表"])
            field_name = self._pick(row, ["字段名", "field_name", "字段"])
            if not table_name or not field_name:
                continue
            tables.setdefault(table_name, {"table_name": table_name, "domain": "", "description": "", "fields": []})
            tables[table_name]["fields"].append(self._normalize_field({
                "name": field_name,
                "type": self._pick(row, ["字段类型", "type", "类型"]),
                "description": self._pick(row, ["字段说明", "comment", "说明"]),
                "classification": self._pick(row, ["字段分类", "classification", "分类"]),
                "dimension": self._pick(row, ["维度", "dimension"]),
            }))
        return tables

    def _build_dimensions(self, processes: List[Dict[str, Any]], ods_tables: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        dimensions: Dict[str, Dict[str, Any]] = {}
        for process in processes:
            for dim_name in process.get("dimensions", []):
                entity = self._normalize_name(dim_name)
                dimensions.setdefault(entity, {
                    "name": dim_name,
                    "entity": entity,
                    "business_key": f"{entity}_id",
                    "attributes": [],
                    "source_tables": [],
                    "scd_type": None,
                })

        for table_name, table in ods_tables.items():
            for field in table.get("fields", []):
                dim_name = field.get("dimension")
                if not dim_name:
                    if not self._can_infer_dimension(field):
                        continue
                    dim_name = self._infer_dimension_from_field(field.get("name", ""))
                if not dim_name:
                    continue
                entity = self._normalize_name(dim_name)
                dim = dimensions.setdefault(entity, {
                    "name": dim_name,
                    "entity": entity,
                    "business_key": f"{entity}_id",
                    "attributes": [],
                    "source_tables": [],
                    "scd_type": None,
                })
                if table_name not in dim["source_tables"]:
                    dim["source_tables"].append(table_name)
                if field["name"].endswith("_id") or field.get("classification") in {"business_key", "foreign_key", "date_key"}:
                    dim["business_key"] = field["name"]
                elif self._is_dimension_attribute(field):
                    dim["attributes"].append({
                        "name": field["name"],
                        "source_field": field["name"],
                        "type": field.get("type") or "STRING",
                        "description": field.get("description") or field["name"],
                    })

        for dim in dimensions.values():
            dim["attributes"] = self._dedupe_fields(dim["attributes"])
            dim["scd_type"] = dim["scd_type"] or self._infer_scd_type(dim, ods_tables)
            if not dim["attributes"] and dim["entity"] != "date":
                self._warn(f"维度缺少属性字段: {dim['name']}")
        return list(dimensions.values())

    def _normalize_process(self, item: Dict[str, Any]) -> Dict[str, Any]:
        domain = item.get("domain") or item.get("数据域") or ""
        process = item.get("business_process") or item.get("process") or item.get("业务过程") or ""
        measures = item.get("measures") or []
        if isinstance(measures, str):
            measures = self._split_measures(measures)
        return {
            "domain": domain,
            "business_process": process,
            "grain": item.get("grain") or item.get("granularity") or item.get("粒度") or "",
            "fact_type": item.get("fact_type") or "transaction",
            "dimensions": self._normalize_list(item.get("dimensions") or item.get("一致性维度") or []),
            "measures": [self._normalize_measure(measure) for measure in measures],
            "source_tables": self._normalize_list(item.get("source_tables") or item.get("源表") or []),
        }

    def _normalize_field(self, field: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": field.get("name") or field.get("field_name") or "",
            "type": field.get("type") or field.get("字段类型") or "STRING",
            "description": field.get("description") or field.get("comment") or field.get("字段说明") or "",
            "classification": field.get("classification") or field.get("字段分类") or "",
            "dimension": field.get("dimension") or field.get("维度") or "",
        }

    def _normalize_measure(self, measure: Any) -> Dict[str, Any]:
        if isinstance(measure, str):
            return {
                "name": self._normalize_name(measure),
                "source_field": self._normalize_name(measure),
                "type": "DECIMAL(18,2)",
                "description": measure,
                "aggregation": "SUM",
            }
        return {
            "name": measure.get("name") or self._normalize_name(measure.get("description", "measure")),
            "source_field": measure.get("source_field") or measure.get("name"),
            "type": measure.get("type") or "DECIMAL(18,2)",
            "description": measure.get("description") or measure.get("name", ""),
            "aggregation": measure.get("aggregation") or "SUM",
        }

    def _validate(self, model: Dict[str, Any]) -> None:
        if not model["processes"]:
            self._warn("未解析到任何业务过程")
        for process in model["processes"]:
            name = process.get("business_process") or "<unknown>"
            if not process.get("grain"):
                self._warn(f"业务过程缺少粒度: {name}")
            if not process.get("dimensions"):
                self._warn(f"业务过程缺少维度: {name}")
            if not process.get("measures"):
                self._warn(f"业务过程缺少度量: {name}")
        for dim in model["dimensions"]:
            if not dim.get("business_key"):
                self._warn(f"维度缺少业务键: {dim.get('name')}")

    def _is_dimension_attribute(self, field: Dict[str, str]) -> bool:
        classification = field.get("classification", "")
        if classification == "dimension_attribute":
            return True
        return not classification or classification in {"attribute", "维度属性"}

    def _can_infer_dimension(self, field: Dict[str, str]) -> bool:
        classification = field.get("classification", "")
        return classification in {"foreign_key", "date_key", "dimension_attribute", "attribute", "维度属性"}

    def _infer_dimension_from_field(self, field_name: str) -> str:
        if field_name.endswith("_id"):
            return field_name[:-3]
        if "_" in field_name:
            return field_name.split("_", 1)[0]
        return ""

    def _infer_scd_type(self, dim: Dict[str, Any], ods_tables: Dict[str, Dict[str, Any]]) -> int:
        if dim["entity"] in {"date", "time"}:
            return 1
        for table_name in dim.get("source_tables", []):
            fields = ods_tables.get(table_name, {}).get("fields", [])
            if any(field["name"] in {"update_time", "gmt_modified", "modified_time", "version"} for field in fields):
                return 2
        return 1

    def _normalize_name(self, name: str) -> str:
        name_map = {
            "销售": "sales",
            "库存": "inventory",
            "客户": "customer",
            "商品": "product",
            "店铺": "shop",
            "门店": "shop",
            "日期": "date",
            "时间": "time",
            "地区": "region",
            "供应商": "supplier",
        }
        return name_map.get(str(name).strip(), re.sub(r"[^a-zA-Z0-9_]+", "_", str(name).strip().lower()).strip("_"))

    def _dedupe_fields(self, fields: List[Dict[str, str]]) -> List[Dict[str, str]]:
        seen = set()
        result = []
        for field in fields:
            if field["name"] in seen:
                continue
            seen.add(field["name"])
            result.append(field)
        return result

    def _split_measures(self, value: str) -> List[Dict[str, Any]]:
        return [self._normalize_measure(item) for item in self._split_list(value)]

    def _split_list(self, value: str) -> List[str]:
        return [item.strip() for item in re.split(r"[+,，、;/；]", value or "") if item.strip()]

    def _normalize_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return self._split_list(str(value))

    def _row_has(self, row: Dict[str, str], keys: List[str]) -> bool:
        return all(self._pick(row, [key]) for key in keys)

    def _pick(self, row: Dict[str, str], keys: List[str]) -> str:
        for key in keys:
            if key in row and row[key]:
                return row[key]
        return ""

    def _warn(self, message: str) -> None:
        self.warnings.append(message)
        if self.logger:
            self.logger.warning(message)
