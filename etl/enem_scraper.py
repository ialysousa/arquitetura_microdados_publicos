import requests
import boto3
from io import BytesIO

# Configuração do MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='admin123',
    region_name='us-east-1'
)

# 1. URL direta do ENEM 2023 (você pode adaptar para outro ano se quiser)
zip_url = "https://download.inep.gov.br/microdados/microdados_enem_2023.zip"
zip_filename = zip_url.split("/")[-1]

# 2. Baixa o ZIP
print(f"📥 Baixando {zip_url} ...")
zip_response = requests.get(zip_url)
zip_response.raise_for_status()
print("✅ Download concluído!")

# 3. Cria o bucket bronze se não existir
bucket_name = 'microdados-bronze'
existing = s3.list_buckets()
if bucket_name not in [b['Name'] for b in existing['Buckets']]:
    s3.create_bucket(Bucket=bucket_name)

# 4. Envia o ZIP para o MinIO
key = f"enem_bronze/{zip_filename}"
print(f"📤 Enviando para MinIO: {bucket_name}/{key}")
s3.upload_fileobj(BytesIO(zip_response.content), bucket_name, key)
print("🏁 Envio concluído!")
