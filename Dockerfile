FROM python:3

WORKDIR /usr/src/babyapp


# Install Vault CLI
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://releases.hashicorp.com/vault/1.13.3/vault_1.13.3_linux_amd64.zip && \
    unzip vault_1.13.3_linux_amd64.zip && \
    mv vault /usr/local/bin/ && \
    rm vault_1.13.3_linux_amd64.zip
    
COPY vault/ /usr/src/babyapp/vault/
COPY main.py /usr/src/babyapp
COPY requirements.txt /usr/src/babyapp

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
