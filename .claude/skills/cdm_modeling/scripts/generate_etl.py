"""
generate_etl.py - ETL脚本生成模块
========================================
根据DIM/DWD设计生成对应的ETL加载脚本
"""

from pathlib import Path
from typing import Dict, List
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class ETLScriptGenerator:
    """ETL脚本生成器"""

    def __init__(self, dim_designs: Dict, dwd_designs: Dict, rules_dir: Path, templates_dir: Path, output_dir: Path, logger=None):
        self.dim_designs = dim_designs
        self.dwd_designs = dwd_designs
        self.rules_dir = Path(rules_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger

    def generate(self):
        """生成所有ETL脚本"""

        # 生成 DIM ETL
        self._generate_dim_etl()

        # 生成 DWD ETL
        self._generate_dwd_etl()

    def _generate_dim_etl(self):
        """生成DIM维度表ETL脚本"""

        output_dir = self.output_dir / 'etl' / 'dim'
        output_dir.mkdir(parents=True, exist_ok=True)

        # 配置Jinja2环境
        env = Environment(loader=FileSystemLoader(str(self.templates_dir)))

        for table_name, dim_info in self.dim_designs.items():
            try:
                template = env.get_template('dim_etl.tpl')
            except TemplateNotFound:
                if self.logger:
                    self.logger.warning(f"  ⚠ Template file not found: dim_etl.tpl")
                continue

            # 准备维度属性字段
            attributes = dim_info.get('attributes', [])
            fields = [{'name': attr['name'], 'type': attr['type'], 'description': attr['description']} for attr in attributes]

            context = {
                'table_name': table_name,
                'entity': dim_info['entity'],
                'business_key': dim_info['business_key'],
                'scd_type': dim_info['scd_type'],
                'fields': fields,
                'domain': 'default',  # 临时使用默认，后续从总线矩阵获取
            }

            # 渲染模板
            sql = template.render(context)

            # 写入输出文件
            output_file = output_dir / f"load_{table_name}.sql"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql)

            if self.logger:
                self.logger.success(f"  ✓ {output_file.name}")

    def _generate_dwd_etl(self):
        """生成DWD事实表ETL脚本"""

        output_dir = self.output_dir / 'etl' / 'dwd'
        output_dir.mkdir(parents=True, exist_ok=True)

        # 配置Jinja2环境
        env = Environment(loader=FileSystemLoader(str(self.templates_dir)))

        for table_name, dwd_info in self.dwd_designs.items():
            try:
                template = env.get_template('dwd_etl.tpl')
            except TemplateNotFound:
                if self.logger:
                    self.logger.warning(f"  ⚠ Template file not found: dwd_etl.tpl")
                continue

            context = {
                'table_name': table_name,
                'entity': dwd_info['business_process'],
                'domain': dwd_info['domain'],
                'dimensions': [{'entity': d} for d in dwd_info['dimensions']],
                'measures': dwd_info['measures'],
                'table_comment': f"事实表: {dwd_info['domain']}-{dwd_info['business_process']}",
            }

            # 渲染模板
            sql = template.render(context)

            # 写入输出文件
            output_file = output_dir / f"load_{table_name}.sql"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql)

            if self.logger:
                self.logger.success(f"  ✓ {output_file.name}")
