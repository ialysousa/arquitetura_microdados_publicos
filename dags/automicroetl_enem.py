from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os
import requests
from zipfile import ZipFile

# ========================
# Diretórios (ajustado ao docker-compose)
# ========================
DOWNLOAD_DIR = '/app/data/bronze'
SILVER_DIR = '/app/data/silver'
GOLD_DIR = '/app/data/gold'
FILENAME = 'microdados_enem_2023.zip'
URL_BASE = f'https://download.inep.gov.br/microdados/microdados_enem_2023.zip'  # substitua se necessário

# ========================
# Funções Python
# ========================

def verificar_novos_dados():
    """Verifica se o arquivo já existe na camada bronze."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    path = os.path.join(DOWNLOAD_DIR, FILENAME)
    if os.path.exists(path):
        print("Arquivo já está presente. Nenhum novo dado detectado.")
        return False
    else:
        print("Novo arquivo detectado.")
        return True

def baixar_dados():
    """Faz o download do arquivo ZIP do ENEM."""
    response = requests.get(URL_BASE, stream=True)
    destino = os.path.join(DOWNLOAD_DIR, FILENAME)

    with open(destino, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Download concluído: {destino}")

def descompactar_e_padronizar():
    """Extrai os dados da camada bronze e os salva na prata."""
    zip_path = os.path.join(DOWNLOAD_DIR, FILENAME)
    os.makedirs(SILVER_DIR, exist_ok=True)

    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(SILVER_DIR)

    print(f"Descompactação concluída para: {SILVER_DIR}")

def mover_para_ouro():
    """Move os arquivos da camada prata para a camada ouro."""
    os.makedirs(GOLD_DIR, exist_ok=True)
    arquivos = os.listdir(SILVER_DIR)

    for file in arquivos:
        src = os.path.join(SILVER_DIR, file)
        dst = os.path.join(GOLD_DIR, file)
        if os.path.isfile(src):
            os.rename(src, dst)

    print(f"Arquivos movidos para camada ouro: {GOLD_DIR}")

# ========================
# Configuração da DAG
# ========================
default_args = {
    'owner': 'ialy',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='automicroetl_enem',
    default_args=default_args,
    description='Pipeline AutoMicroETL para microdados do ENEM',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['enem', 'automicroetl'],
) as dag:

    verificar = PythonOperator(
        task_id='verificar_novos_dados',
        python_callable=verificar_novos_dados
    )

    baixar = PythonOperator(
        task_id='baixar_dados',
        python_callable=baixar_dados
    )

    descompactar = PythonOperator(
        task_id='descompactar_e_padronizar',
        python_callable=descompactar_e_padronizar
    )

    mover = PythonOperator(
        task_id='mover_para_ouro',
        python_callable=mover_para_ouro
    )

    # Orquestração
    verificar >> baixar >> descompactar >> mover
