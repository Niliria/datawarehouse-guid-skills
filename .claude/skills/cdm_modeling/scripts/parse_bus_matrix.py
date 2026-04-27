"""
parse_bus_matrix.py - 总线矩阵解析模块
========================================
从CSV文件解析业务流程矩阵
"""

import csv
from pathlib import Path
from typing import Dict, List


class BusMatrixParser:
    """总线矩阵解析器"""
    
    def __init__(self, bus_matrix_file: str, logger=None):
        self.bus_matrix_file = Path(bus_matrix_file)
        self.logger = logger
    
    def parse(self) -> Dict[str, Dict]:
        """
        解析总线矩阵CSV文件
        
        CSV格式预期：
        数据域,业务过程,粒度,一致性维度,备注
        销售,门店销售,订单,店铺+日期+商品+客户,
        
        Returns:
            Dict: {
                '销售_门店销售': {
                    'domain': '销售',
                    'business_process': '门店销售',
                    'granularity': '订单',
                    'dimensions': ['店铺', '日期', '商品', '客户'],
                    'remarks': '...'
                },
                ...
            }
        """
        
        if not self.bus_matrix_file.exists():
            if self.logger:
                self.logger.error(f"文件不存在: {self.bus_matrix_file}")
            return {}
        
        bus_matrix = {}
        
        try:
            with open(self.bus_matrix_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    domain = row.get('数据域', '').strip()
                    process = row.get('业务过程', '').strip()
                    
                    if not domain or not process:
                        continue
                    
                    key = f"{domain}_{process}"
                    
                    # 解析一致性维度（用+号分隔）
                    dims_str = row.get('一致性维度', '').strip()
                    dimensions = [d.strip() for d in dims_str.split('+') if d.strip()]
                    
                    bus_matrix[key] = {
                        'domain': domain,
                        'business_process': process,
                        'granularity': row.get('粒度', '').strip(),
                        'dimensions': dimensions,
                        'remarks': row.get('备注', '').strip()
                    }
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"解析失败: {e}")
            return {}
        
        return bus_matrix
