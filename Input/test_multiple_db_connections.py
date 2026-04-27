import yaml
import pymysql
import sqlite3

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

def test_all_connections():
    # 读取配置文件
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    db_configs = config.get('database', {})
    
    print("开始测试数据库连接...\n")
    
    results = {}
    for db_name, db_config in db_configs.items():
        print(f"测试 {db_name} ({db_config.get('type', 'unknown')}):")
        print(f"  配置: {db_config}")
        
        db_type = db_config.get('type')
        
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
        
        results[db_name] = {'success': success, 'message': message}
        
        if success:
            print(f"  ✅ 连接成功! {message}")
        else:
            print(f"  ❌ 连接失败: {message}")
        print()
    
    # 输出总结
    print("测试总结:")
    print("-" * 50)
    for db_name, result in results.items():
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"{db_name}: {status}")
    print("-" * 50)

if __name__ == "__main__":
    test_all_connections()