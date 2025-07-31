import boto3
import zipfile
import os
import io

# Configurações do MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='admin123',
    region_name='us-east-1'
)

bronze_bucket = "microdados-bronze"
silver_bucket = "microdados-silver"
bronze_prefix = "enem_bronze/"
silver_prefix = "enem/"

# Cria bucket silver se não existir
existing_buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
if silver_bucket not in existing_buckets:
    s3.create_bucket(Bucket=silver_bucket)
    print(f"🪣 Bucket '{silver_bucket}' criado.")

# Lista arquivos .zip na bronze
print("📦 Procurando arquivos .zip no bucket bronze...")
objects = s3.list_objects_v2(Bucket=bronze_bucket, Prefix=bronze_prefix)

if 'Contents' not in objects:
    raise Exception("Nenhum arquivo encontrado na camada bronze.")

for obj in objects['Contents']:
    key = obj['Key']
    if not key.endswith('.zip'):
        continue

    print(f"📥 Baixando {key} do bucket bronze...")
    zip_obj = s3.get_object(Bucket=bronze_bucket, Key=key)
    zip_content = zip_obj['Body'].read()

    # Extrai e envia para o bucket silver
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
        for file_name in zip_file.namelist():
            print(f"📄 Extraindo: {file_name}")
            extracted = zip_file.read(file_name)

            # Envia para MinIO no bucket silver
            key_silver = silver_prefix + file_name
            s3.put_object(Bucket=silver_bucket, Key=key_silver, Body=extracted)
            print(f"✅ Enviado para: {silver_bucket}/{key_silver}")

print("✨ Processo de criação da camada silver concluído.")
