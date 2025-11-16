# Base da Lambda Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Instalar dependências de sistema necessárias para pandas/pyarrow
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    python3-devel \
    libffi-devel \
    openssl-devel \
    && yum clean all

# Copiar somente requirements primeiro (melhor cache)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar o código da Lambda
COPY . ${LAMBDA_TASK_ROOT}

# Definir o handler
CMD ["main.lambda_handler"]
