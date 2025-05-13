# 📊 Pipeline de Microdados ENEM com Docker + MinIO

Este projeto implementa um pipeline local e automatizado para extrair, organizar e armazenar microdados públicos do ENEM. A arquitetura segue o padrão de camadas **Bronze → Silver → Gold**, usando contêineres Docker, armazenamento em MinIO e scripts em Python.

---

## 📁 Estrutura de Diretórios

```
microdados_pipeline/
├── data/
├── etl/
│   ├── enem_scraper.py       # Bronze
│   ├── silver_loader.py      # Silver
│   ├── gold_loader.py        # Gold
├── notebooks/                # Análises no Jupyter
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/microdados_pipeline.git
cd microdados_pipeline
```

---

### 2. Suba o ambiente com Docker

```bash
docker-compose up --build
```

> Isso irá iniciar três contêineres:
>
> * `minio`: armazenamento de arquivos (S3-like)
> * `etl_runner`: para executar os scripts Python
> * `jupyter`: para análise e visualização

---

### 3. Acesse a interface do MinIO

* Abra [http://localhost:9001](http://localhost:9001)
* Login: `admin`
* Senha: `admin123`

Você poderá visualizar os buckets:

* `microdados-bronze`
* `microdados-silver`
* `microdados-gold`

---

### 4. Acesse o Jupyter Notebook (opcional)

Abra [http://localhost:8888](http://localhost:8888) e use o token gerado no terminal para acessar.

---

## 🔁 Etapas do Pipeline

### 🔹 Bronze – Download e Armazenamento

```bash
docker exec -it etl_runner bash
cd etl
python enem_scraper.py
```

* Faz o scraping do site do INEP
* Baixa o ZIP dos microdados do ENEM
* Armazena no bucket `microdados-bronze` na pasta `enem_bronze/`

---

### 🔸 Silver – Extração e Organização

```bash
python silver_loader.py
```

* Extrai os arquivos do `.zip`
* Envia os arquivos descompactados para `microdados-silver`, em subpastas como:

  * `enem/DADOS/`
  * `enem/inputs/`
  * `enem/provas/` etc.

---

### 🟡 Gold – Tratamento e Padronização

```bash
python gold_loader.py
```

* Lê os arquivos relevantes da pasta `enem/DADOS/`
* Realiza tratamento leve (remove nulos, padroniza nomes de colunas)
* Divide arquivos grandes em pedaços (ex: `MICRODADOS_ENEM_2023.csv`)
* Armazena as versões tratadas no bucket `microdados-gold/enem/`

---

## 🧪 Exemplos de Análises (Jupyter)

Você pode usar os arquivos da camada Gold dentro do Jupyter para fazer análises, filtros, visualizações e machine learning com:

```python
import pandas as pd
df = pd.read_csv("path/para/arquivo_tratado.csv")
```

---

## 🛠️ Tecnologias Utilizadas

* Docker & Docker Compose
* Python 3.10
* MinIO (S3 local)
* Pandas
* Requests & BeautifulSoup
* Jupyter Notebook

---

## 💡 Potencial de Inovação

Esta arquitetura permite:

* Automatização da coleta e estruturação de microdados públicos
* Simulação local de um Data Lake
* Adoção de boas práticas em Engenharia de Dados (camadas, reprodutibilidade, modularidade)
* Reutilização para outras bases públicas (ex: CAGED, PNAD, etc.)
