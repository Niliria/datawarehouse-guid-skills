"""
generate_dwd.py - DWD事实表生成模块
========================================
根据业务流程生成DWD事实表设计，输出DDL脚本
"""

from pathlib import Path
from typing import Dict, List
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class FactTableGenerator:
    """事实表生成器"""
    
    def __init__(self, bus_matrix: Dict, dim_designs: Dict, rules_dir: Path, templates_dir: Path, output_dir: Path = None, logger=None):
        self.bus_matrix = bus_matrix
        self.dim_designs = dim_designs
        self.rules_dir = Path(rules_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir) if output_dir else None
        self.logger = logger
        self.dwd_rules = self._load_rules('dwd_rules.yaml')
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
        生成DWD事实表设计，并输出DDL脚本
        
        根据总线矩阵中的业务过程生成对应的事实表
        
        Returns:
            Dict: {
                'dwd_sales_order_di': {
                    'table_name': 'dwd_sales_order_di',
                    'domain': 'sales',
                    'business_process': 'order',
                    'dimensions': ['customer', 'product', 'shop', 'date'],
                    'measures': [
                        {'name': 'order_amount', 'type': 'DECIMAL(18,2)', 'aggregation': 'SUM'},
                        ...
                    ],
                    'grain': 'order_id'
                },
                ...
            }
        """
        
        dwd_designs = {}
        
        # 从总线矩阵生成事实表
        for key, process_info in self.bus_matrix.items():
            
            domain = process_info['domain']
            process = process_info['business_process']
            dimensions = process_info['dimensions']
            
            # 生成表名 (e.g., dwd_sales_order_di)
            domain_en = self._normalize_name(domain)
            process_en = self._normalize_name(process)
            table_name = f"dwd_{domain_en}_{process_en}_di"
            
            # 构建维度外键列表
            dim_fks = [self._normalize_name(d) for d in dimensions]
            # 总是添加日期维度
            if 'date' not in dim_fks:
                dim_fks.append('date')
            
            # 构建度量值列表 (示例)
            measures = [
                {'name': 'quantity', 'type': 'BIGINT', 'description': '数量', 'aggregation': 'SUM'},
                {'name': 'amount', 'type': 'DECIMAL(18,2)', 'description': '金额', 'aggregation': 'SUM'},
            ]
            
            # 创建事实表设计
            dwd_designs[table_name] = {
                'table_name': table_name,
                'domain': domain_en,
                'business_process': process_en,
                'business_key': f'{process_en}_id',
                'dimensions': dim_fks,
                'measures': measures,
                'grain': f'{process_en}_id',
                'estimated_size': 'large'  # 事实表通常较大
            }
            
            if self.logger:
                dims_str = ', '.join(dim_fks)
                self.logger.success(f"  ✓ {table_name}")
                self.logger.info(f"      维度: {dims_str}")
        
        # 生成DDL脚本
        if self.output_dir:
            self._generate_ddl(dwd_designs)
        
        return dwd_designs
    
    def _generate_ddl(self, dwd_designs: Dict[str, Dict]) -> None:
        """生成事实表DDL脚本"""
        output_dir = self.output_dir / 'ddl' / 'dwd'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置Jinja2环境
        env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        
        try:
            template = env.get_template('dwd_ddl.tpl')
        except TemplateNotFound:
            if self.logger:
                self.logger.warning(f"  ⚠ Template file not found: dwd_ddl.tpl")
            return
        
        # 为每个事实表生成DDL
        for table_name, dwd_info in dwd_designs.items():
            # 准备模板变量
            context = {
                'table_name': table_name,
                'entity': dwd_info['business_process'],
                'domain': dwd_info['domain'],
                'business_process': dwd_info['business_process'],
                'grain': dwd_info['grain'],
                'dimensions': [{'entity': d} for d in dwd_info['dimensions']],
                'measures': dwd_info['measures'],
                'table_comment': f"事实表: {dwd_info['domain']}-{dwd_info['business_process']}",
            }
            
            # 渲染模板
            try:
                sql = template.render(context)
                
                # 写出DDL文件
                output_file = output_dir / f"{table_name}.sql"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(sql)
                
                if self.logger:
                    self.logger.success(f"  ✓ Generated DDL: {output_file.name}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"  ⚠ Failed to render {table_name}: {e}")
    
    def _normalize_name(self, name: str) -> str:
        """规范化名称为英文小写"""
        name_map = {
            '销售': 'sales',
            '门店': 'shop',
            '库存': 'inventory',
            '营销': 'marketing',
            '订单': 'order',
            '发货': 'shipment',
            '支付': 'payment',
            '客户': 'customer',
            '商品': 'product',
            '店铺': 'shop',
            '日期': 'date',
            '地区': 'region',
        }
        return name_map.get(name, name.lower())
