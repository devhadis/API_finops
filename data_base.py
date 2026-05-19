import mysql.connector
from mysql.connector import Error

def create_Data_Base():
    
    connect = None
    cursor = None
    
    config = {
        'host': 'localhost',
        'user': '',
        'password': ''
    }
    company_name = "" #Não esqueça de colocar o nome da empresa
    
    data_base_name = "db_finops_turbonomic_" + company_name
    
    
    try:
        
        connect =  mysql.connector.connect(**config)
        
        cursor. execute(f"CREATE DATABASE IF NOT EXISTS {data_base_name}")
        
        print(f"Banco {data_base_name} CRIADO COM SUCESSO !!")
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {data_base_name}")
        
        cursor.execute(f"USE {data_base_name}")
        
        sql = """
        
        CREATE TABLE IF NOT EXISTS parking_mensal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_registro DATETIME NOT NULL,
            entity_type VARCHAR(100),
            action_type VARCHAR(100),
            entity VARCHAR(255),
            details TEXT,
            account_name VARCHAR(100),
            resource_group VARCHAR(100),
            execution_saving_mensal VARCHAR(100),
            mode VARCHAR(50),
            user_Name VARCHAR(100),
            savings_per_hr DECIMAL(18, 7) DEFAULT 0.0,
            savings_per_mes DECIMAL(18, 7) DEFAULT 0.0,
            tag_xpca VARCHAR(100)
        );


        CREATE TABLE IF NOT EXISTS savings_mensal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_registro DATETIME NOT NULL,
            entity_type VARCHAR(100),
            action_type VARCHAR(100),
            entity VARCHAR(255),
            details TEXT,
            account_name VARCHAR(100),
            resource_group VARCHAR(100),
            execution_saving_mensal VARCHAR(100),
            mode VARCHAR(50),
            user_Name VARCHAR(100),
            savings_per_hr DECIMAL(18, 7) DEFAULT 0.0,
            savings_per_mes DECIMAL(18, 7) DEFAULT 0.0,
            tag_xpca VARCHAR(100)
        );


        CREATE TABLE IF NOT EXISTS potencial_economico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_registro DATETIME NOT NULL,
            action_uuid VARCHAR(100),
            entity_type VARCHAR(100),
            action_type VARCHAR(100),
            entity_name VARCHAR(255),
            details TEXT,
            account_name VARCHAR(100),
            resource_group VARCHAR(100),
            category VARCHAR(100),
            mode VARCHAR(50),
            saving_per_hr DECIMAL(18, 7) DEFAULT 0.0,
            saving_per_mes DECIMAL(18, 7) DEFAULT 0.0,
            tag_xpca VARCHAR(100)
        );
        
        """
        

        cursor.execute(sql)
        
    except Error as e:
        print(f"Erro: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connect and connect.is_connected():
            connect.close()
if __name__ == "__main__":
    create_Data_Base()
    







