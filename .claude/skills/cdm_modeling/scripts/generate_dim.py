"""
generate_dim.py - DIM维度表生成模块
========================================
根据总线矩阵生成DIM维度表设计，输出DDL脚本
"""

from pathlib import Path
from typing import Dict, List
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class DimensionGenerator:
    """维度表生成器"""
    
    def __init__(self, bus_matrix: Dict, rules_dir: Path, templates_dir: Path, output_dir: Path = None, logger=None):
        self.bus_matrix = bus_matrix
        self.rules_dir = Path(rules_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir) if output_dir else None
        self.logger = logger
        self.dim_rules = self._load_rules('dim_rules.yaml')
        self.naming_rules = self._load_rules('naming_rules.yaml')
    
    def _load_rules(self, rule_file: str) -> Dict:
        """加载规则文件"""
        rule_path = self.rules_dir / rule_file
        if rule_path.exists():
            with open(rule_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def generate(self) -> Dict[str, Dict]:
        """
        生成DIM维度表设计，并输出DDL脚本
        
        Returns:
            Dict: {
                'dim_customer': {
                    'table_name': 'dim_customer',
                    'entity': 'customer',
                    'scd_type': 2,
                    'business_key': 'customer_id',
                    'attributes': [...],
                    'scd_fields': [...]
                },
                ...
            }
        """
        
        dim_designs = {}
        
        # 从总线矩阵中提取所有维度
        all_dimensions = set()
        for process_info in self.bus_matrix.values():
            all_dimensions.update(process_info.get('dimensions', []))
        
        if self.logger:
            self.logger.info(f"  识别到 {len(all_dimensions)} 个维度")
        
        # 为每个维度创建设计
        for dim_name in sorted(all_dimensions):
            
            # 生成表名 (e.g., dim_customer)
            entity_name = self._normalize_name(dim_name)
            table_name = f"dim_{entity_name}"
            
            # 确定SCD策略 (默认Type II)
            scd_type = self._determine_scd_type(dim_name)
            
            # 创建维度设计
            dim_designs[table_name] = {
                'table_name': table_name,
                'entity': entity_name,
                'scd_type': scd_type,
                'business_key': f'{entity_name}_id',
                'attributes': [
                    {'name': f'{entity_name}_name', 'type': 'STRING', 'description': f'{dim_name}名称'},
                    {'name': f'{entity_name}_code', 'type': 'STRING', 'description': f'{dim_name}编码'},
                ],
                'scd_fields': (
                    ['begin_date', 'end_date', 'is_active'] if scd_type == 2 else []
                ),
                'estimated_size': 'small'   # 维度通常较小
            }
            
            if self.logger:
                self.logger.success(f"  ✓ {table_name} (SCD Type {scd_type})")
        
        # 生成DDL脚本
        if self.output_dir:
            self._generate_ddl(dim_designs)
        
        return dim_designs
    
    def _generate_ddl(self, dim_designs: Dict[str, Dict]) -> None:
        """生成维度表DDL脚本"""
        output_dir = self.output_dir / 'ddl' / 'dim'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置Jinja2环境
        env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        
        try:
            template = env.get_template('dim_ddl.tpl')
        except TemplateNotFound:
            if self.logger:
                self.logger.warning(f"  ⚠ Template file not found: dim_ddl.tpl")
            return
        
        # 为每个维度表生成DDL
        for table_name, dim_info in dim_designs.items():
            # 准备模板变量
            context = {
                'table_name': table_name,
                'entity': dim_info['entity'],
                'scd_type': dim_info['scd_type'],
                'business_key': dim_info['business_key'],
                'attributes': dim_info['attributes'],
                'scd_fields': dim_info['scd_fields'],
                'table_comment': f"维度表: {dim_info['entity']}",
            }
            
            # 渲染模板
            try:
                sql = template.render(context)
                
                # 写出DDL文件
                output_file = output_dir / f"{table_name}_scd{dim_info['scd_type']}.sql"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(sql)
                
                if self.logger:
                    self.logger.success(f"  ✓ Generated DDL: {output_file.name}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"  ⚠ Failed to render {table_name}: {e}")
    
    def _normalize_name(self, name: str) -> str:
        """规范化名称为英文小写"""
        # 简单映射示例
        name_map = {
            '客户': 'customer',
            '商品': 'product',
            '店铺': 'shop',
            '日期': 'date',
            '地区': 'region',
            '供应商': 'supplier',
        }
        return name_map.get(name, name.lower())
    
    def _determine_scd_type(self, dim_name: str) -> int:
        """
        根据维度名称确定SCD策略
        
        规则：
        - 与时间相关 → Type I (date/time)
        - 需要追踪历史 → Type II (customer/product)
        - 其他 → Type I
        """
        
        # Type I: 时间维度、静态维度
        type_1_keywords = ['date', 'time', 'calendar', '日期', '时间']
        if any(keyword in dim_name.lower() for keyword in type_1_keywords):
            return 1
        
        # Type II: 需要历史追踪的维度 (默认)
        return 2
