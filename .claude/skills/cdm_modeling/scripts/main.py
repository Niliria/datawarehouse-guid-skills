"""
CDM建模 Skill - 主入口脚本 (main.py)
========================================
协调所有子模块执行完整的数仓建模流程
"""

import sys
from pathlib import Path
from typing import Dict
import yaml
from datetime import datetime
import csv

# 导入子模块
try:
    from parse_bus_matrix import BusMatrixParser
    from generate_dim import DimensionGenerator
    from generate_dwd import FactTableGenerator
    from generate_etl import ETLScriptGenerator
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保所有脚本都在同一目录下")
    sys.exit(1)


class Logger:
    """简单日志器"""
    
    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"✅ {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"⚠️  {msg}")
    
    @staticmethod
    def error(msg):
        print(f"❌ {msg}")


class CDMModelingSkill:
    """CDM建模 Skill - 主类"""
    
    def __init__(self, config_file):
        self.logger = Logger()
        self.config = self._load_config(config_file)
        self.project_root = Path(__file__).parent.parent
        
    def _load_config(self, config_file):
        """加载技能配置"""
        config_path = Path(config_file)
        if not config_path.exists():
            self.logger.error(f"配置文件不存在: {config_file}")
            sys.exit(1)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            sys.exit(1)
    
    def run(self):
        """执行完整的建模流程"""
        
        self.logger.info("=" * 60)
        self.logger.info("CDM 建模 Skill v1.0")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Phase 1: 解析总线矩阵
            self.logger.info("\n📋 Phase 1: 解析总线矩阵...")
            bus_matrix_parser = BusMatrixParser(
                bus_matrix_file=self.config['input']['bus_matrix'],
                logger=self.logger
            )
            bus_matrix = bus_matrix_parser.parse()
            self.logger.success(f"解析完成: {len(bus_matrix)} 个业务过程")
            
            # Phase 2: 生成DIM维度表设计
            self.logger.info("\n📊 Phase 2: 生成DIM维度表...")
            dim_generator = DimensionGenerator(
                bus_matrix=bus_matrix,
                rules_dir=self.project_root / 'rules',
                templates_dir=self.project_root / 'templates',
                output_dir=Path(self.config['output']['target_dir']),
                logger=self.logger
            )
            dim_designs = dim_generator.generate()
            self.logger.success(f"生成完成: {len(dim_designs)} 个维度表")
            
            # Phase 3: 生成DWD事实表设计
            self.logger.info("\n📈 Phase 3: 生成DWD事实表...")
            dwd_generator = FactTableGenerator(
                bus_matrix=bus_matrix,
                dim_designs=dim_designs,
                rules_dir=self.project_root / 'rules',
                templates_dir=self.project_root / 'templates',
                output_dir=Path(self.config['output']['target_dir']),
                logger=self.logger
            )
            dwd_designs = dwd_generator.generate()
            self.logger.success(f"生成完成: {len(dwd_designs)} 个事实表")
            
            # Phase 4: 生成ETL脚本
            self.logger.info("\n🔧 Phase 4: 生成ETL脚本...")
            etl_generator = ETLScriptGenerator(
                dim_designs=dim_designs,
                dwd_designs=dwd_designs,
                rules_dir=self.project_root / 'rules',
                templates_dir=self.project_root / 'templates',
                output_dir=Path(self.config['output']['target_dir']),
                logger=self.logger
            )
            etl_generator.generate()
            self.logger.success("ETL脚本生成完成")
            
            # Phase 5: 生成设计文档
            self.logger.info("\n📚 Phase 5: 生成设计文档...")
            self._generate_docs(dim_designs, dwd_designs)
            self.logger.success("设计文档生成完成")
            
            # 完成时间统计
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self.logger.info("\n" + "=" * 60)
            self.logger.success(f"✨ 全部完成! (耗时 {elapsed_time:.2f} 秒)")
            self.logger.info("=" * 60)
            
            # 输出总结
            self._print_summary(dim_designs, dwd_designs)
            
            return True
            
        except Exception as e:
            self.logger.error(f"执行失败: {e}")
            return False
    
    def _generate_docs(self, dim_designs, dwd_designs):
        """生成模型清单 - CSV格式"""
        # 从配置读取文档输出目录
        doc_dir = Path(self.config['output']['directories']['docs'])
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成DIM表清单 CSV
        dim_csv_file = doc_dir / 'dim_list.csv'
        self._generate_dim_csv(dim_csv_file, dim_designs)
        if self.logger:
            self.logger.success(f"  ✓ Generated Catalog: dim_list.csv")
        
        # 生成DWD表清单 CSV
        dwd_csv_file = doc_dir / 'dwd_list.csv'
        self._generate_dwd_csv(dwd_csv_file, dwd_designs)
        if self.logger:
            self.logger.success(f"  ✓ Generated Catalog: dwd_list.csv")
    
    def _generate_dim_csv(self, csv_file: Path, dim_designs: Dict):
        """生成DIM表清单CSV - 新格式：包含表元信息和字段详情"""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 遍历每个维度表
            for table_name in sorted(dim_designs.keys()):
                dim_info = dim_designs[table_name]
                
                # 写入表元信息行
                writer.writerow(['模型名', table_name])
                writer.writerow(['中文名', f"维度表-{dim_info['entity']}"])
                writer.writerow(['数据来源', 'ODS'])
                writer.writerow(['主题', dim_info['entity']])
                writer.writerow(['层级', 'DIM'])
                writer.writerow(['说明', f"维度表: {dim_info['entity']}, SCD Type {dim_info['scd_type']}"])
                writer.writerow(['分区字段', 'pt'])
                writer.writerow([])  # 空行分隔
                
                # 写入字段说明头
                writer.writerow(['字段', '字段名', '字段类型', '字段说明', '数据来源', '是否为空', '维度'])
                
                # 业务键字段
                writer.writerow(['', dim_info['business_key'], 'VARCHAR(40)', f"{dim_info['entity']}ID", '首取', 'N', 'Y'])
                
                # 属性字段
                for attr in dim_info['attributes']:
                    writer.writerow(['', attr['name'], 'STRING', attr['description'], '首取', 'N', 'Y'])
                
                # SCD字段
                if dim_info['scd_type'] == 2:
                    for scd_field in dim_info['scd_fields']:
                        if scd_field == 'begin_date':
                            writer.writerow(['', 'begin_date', 'STRING', '生效日期', '首取', 'N', ''])
                        elif scd_field == 'end_date':
                            writer.writerow(['', 'end_date', 'STRING', '失效日期', '首取', 'Y', ''])
                        elif scd_field == 'is_active':
                            writer.writerow(['', 'is_active', 'INT', '是否有效', '首取', 'N', ''])
                
                # 审计字段
                writer.writerow(['', 'etl_insert_time', 'DATETIME', 'ETL插入时间', 'ETL', 'N', ''])
                writer.writerow(['', 'etl_update_time', 'DATETIME', 'ETL更新时间', 'ETL', 'Y', ''])
                writer.writerow(['', 'pt', 'STRING', '分区日期', 'ETL', 'N', ''])
                writer.writerow([])  # 空行分隔
                writer.writerow([])  # 空行分隔
    
    def _generate_dwd_csv(self, csv_file: Path, dwd_designs: Dict):
        """生成DWD表清单CSV - 新格式：包含表元信息和字段详情"""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 遍历每个事实表
            for table_name in sorted(dwd_designs.keys()):
                dwd_info = dwd_designs[table_name]
                
                # 写入表元信息行
                writer.writerow(['模型名', table_name])
                writer.writerow(['中文名', f"事实表-{dwd_info['business_process']}"])
                writer.writerow(['数据来源', f"ODS-{dwd_info['domain']}"])
                writer.writerow(['主题', dwd_info['domain']])
                writer.writerow(['层级', 'DWD'])
                writer.writerow(['说明', f"事实表: {dwd_info['domain']}-{dwd_info['business_process']}"])
                writer.writerow(['分区字段', 'pt'])
                writer.writerow([])  # 空行分隔
                
                # 写入字段说明头
                writer.writerow(['字段', '字段名', '字段类型', '字段说明', '数据来源', '是否为空', '维度', '度量'])
                
                # 维度外键字段
                for dim in dwd_info['dimensions']:
                    writer.writerow(['', dim, 'VARCHAR(40)', f"{dim}引用", '首取', 'N', 'Y', ''])
                
                # 度量值字段
                for measure in dwd_info['measures']:
                    # 处理度量值（可能是字典或字符串）
                    if isinstance(measure, dict):
                        measure_name = measure.get('name', 'unknown')
                        measure_desc = measure.get('description', measure_name)
                    else:
                        measure_name = measure
                        measure_desc = measure
                    writer.writerow(['', measure_name, 'DECIMAL(18,2)', measure_desc, '计算', 'N', '', 'Y'])
                
                # 业务标志字段
                writer.writerow(['', 'is_valid', 'INT', '是否有效', '首取', 'N', '', ''])
                
                # 审计字段
                writer.writerow(['', 'etl_insert_time', 'DATETIME', 'ETL插入时间', 'ETL', 'N', '', ''])
                writer.writerow(['', 'etl_update_time', 'DATETIME', 'ETL更新时间', 'ETL', 'Y', '', ''])
                writer.writerow(['', 'source_system', 'STRING', '源系统', '首取', 'N', '', ''])
                writer.writerow(['', 'pt', 'STRING', '分区日期', 'ETL', 'N', '', ''])
                writer.writerow([])  # 空行分隔
                writer.writerow([])  # 空行分隔
    
    def _print_summary(self, dim_designs, dwd_designs):
        """输出执行总结"""
        target_dir = self.config['output']['target_dir']
        print(f"\n📊 设计总结:")
        print(f"  • DIM维度表: {len(dim_designs)} 个")
        print(f"  • DWD事实表: {len(dwd_designs)} 个")
        print(f"\n📁 输出目录:")
        print(f"  • DDL表定义: {target_dir}ddl/dim/*, {target_dir}ddl/dwd/*")
        print(f"  • ETL加载脚本: {target_dir}etl/dim/*, {target_dir}etl/dwd/*")
        print(f"  • 表模型清单: {target_dir}docs/dim_list.csv, {target_dir}docs/dwd_list.csv")
        print(f"\n💡 下一步:")
        print(f"  1. 查看 {target_dir}docs/ 中的表模型清单")
        print(f"     - dim_list.csv: 所有维度表信息")
        print(f"     - dwd_list.csv: 所有事实表信息")
        print(f"  2. 执行 {target_dir}ddl/ 中的建表SQL语句")
        print(f"  3. 运行 {target_dir}etl/ 中的ETL脚本加载数据")


def main():
    """主函数"""
    
    # 获取项目根目录 (skill_config.yaml 所在目录)
    project_root = Path(__file__).parent.parent.parent.parent
    config_file = project_root / 'skill_config.yaml'
    
    # 创建Skill实例并运行
    skill = CDMModelingSkill(config_file)
    success = skill.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
