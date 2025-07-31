import boto3
import pandas as pd
import io

# Configurações do MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='admin123',
    region_name='us-east-1'
)

silver_bucket = "microdados-silver"
gold_bucket = "microdados-gold"
silver_prefix = "enem/DADOS/"
gold_prefix = "enem/"

# Cria o bucket gold se não existir
existing_buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
if gold_bucket not in existing_buckets:
    s3.create_bucket(Bucket=gold_bucket)
    print(f"🪣 Bucket '{gold_bucket}' criado.")

# Lista os arquivos CSV da pasta DADOS/
print("📂 Lendo arquivos da camada silver...")
objects = s3.list_objects_v2(Bucket=silver_bucket, Prefix=silver_prefix)

if 'Contents' not in objects:
    raise Exception("Nenhum arquivo encontrado na camada silver.")

for obj in objects['Contents']:
    key = obj['Key']
    print(f"\n🔍 Verificando: {key}")

    # Ignora diretórios ou arquivos não .csv
    if not key.endswith('.csv'):
        print(f"⏭️ Ignorando (extensão não suportada): {key}")
        continue

    # Baixa o conteúdo
    print(f"📥 Lendo {key} do bucket silver...")
    raw = s3.get_object(Bucket=silver_bucket, Key=key)['Body'].read()

    # Define nome base do arquivo
    filename = key.split('/')[-1].replace('.csv', '_tratado')

    try:
        chunk_iter = pd.read_csv(io.BytesIO(raw), sep=';', encoding='latin1', chunksize=100_000)
        for i, chunk in enumerate(chunk_iter):
            chunk.dropna(how='all', inplace=True)
            chunk.columns = [col.strip().lower().replace(' ', '_') for col in chunk.columns]
            out_csv = chunk.to_csv(index=False).encode('utf-8')

            part_key = f"{gold_prefix}{filename}_part{i}.csv"
            s3.put_object(Bucket=gold_bucket, Key=part_key, Body=out_csv)

            print(f"✅ Parte {i} salva como {part_key}")

    except Exception as e:
        print(f"⚠️ Erro ao processar {key}: {e}")
        continue

print("\n🏁 Processo da camada gold concluído.")
