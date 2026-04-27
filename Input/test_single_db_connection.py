import yaml
import pymysql
import sqlite3
import sys

def test_mysql_connection(config):
    """测试MySQL数据库连接"""
    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['dbname'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            version = result['VERSION()']
        
        connection.close()
        return True, f"MySQL版本: {version}"
        
    except Exception as e:
        return False, str(e)

def test_sqlite_connection(config):
    """测试SQLite数据库连接"""
    try:
        connection = sqlite3.connect(config['database'])
        cursor = connection.cursor()
        cursor.execute("SELECT sqlite_version()")
        result = cursor.fetchone()
        version = result[0]
        connection.close()
        return True, f"SQLite版本: {version}"
    except Exception as e:
        return False, str(e)

def test_postgresql_connection(config):
    """测试PostgreSQL数据库连接"""
    try:
        import psycopg2
        connection = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['dbname']
        )
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        result = cursor.fetchone()
        version = result[0]
        connection.close()
        return True, f"PostgreSQL版本: {version}"
    except ImportError:
        return False, "需要安装psycopg2库"
    except Exception as e:
        return False, str(e)

def test_oracle_connection(config):
    """测试Oracle数据库连接"""
    try:
        import cx_Oracle
        dsn = cx_Oracle.makedsn(
            config['host'],
            config['port'],
            service_name=config['service_name']
        )
        connection = cx_Oracle.connect(
            user=config['user'],
            password=config['password'],
            dsn=dsn
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM v$version WHERE ROWNUM = 1")
        result = cursor.fetchone()
        version = result[0]
        connection.close()
        return True, f"Oracle版本: {version}"
    except ImportError:
        return False, "需要安装cx_Oracle库"
    except Exception as e:
        return False, str(e)

def test_sqlserver_connection(config):
    """测试SQL Server数据库连接"""
    try:
        import pyodbc
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config['host']},{config['port']};DATABASE={config['dbname']};UID={config['user']};PWD={config['password']}"
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()
        cursor.execute("SELECT @@VERSION")
        result = cursor.fetchone()
        version = result[0]
        connection.close()
        return True, f"SQL Server版本: {version}"
    except ImportError:
        return False, "需要安装pyodbc库"
    except Exception as e:
        return False, str(e)

def test_single_connection(db_name):
    # 读取配置文件
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    db_configs = config.get('database', {})
    
    if db_name not in db_configs:
        print(f"❌ 数据库配置 '{db_name}' 不存在")
        return False
    
    db_config = db_configs[db_name]
    db_type = db_config.get('type')
    
    print(f"开始测试数据库连接: {db_name} ({db_type})\n")
    print(f"配置信息: {db_config}\n")
    
    if db_type == 'mysql':
        success, message = test_mysql_connection(db_config)
    elif db_type == 'sqlite':
        success, message = test_sqlite_connection(db_config)
    elif db_type == 'postgresql':
        success, message = test_postgresql_connection(db_config)
    elif db_type == 'oracle':
        success, message = test_oracle_connection(db_config)
    elif db_type == 'sqlserver':
        success, message = test_sqlserver_connection(db_config)
    else:
        success, message = False, f"不支持的数据库类型: {db_type}"
    
    if success:
        print(f"✅ 连接成功! {message}")
    else:
        print(f"❌ 连接失败: {message}")
    
    return success

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python test_single_db_connection.py <数据库名称>")
        print("例如: python test_single_db_connection.py primary_mysql")
        sys.exit(1)
    
    db_name = sys.argv[1]
    test_single_connection(db_name)