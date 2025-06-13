# GuardianPro
**Plataforma de Telemedicina por Chat Inteligente com Geração Automatizada de Laudos**

O GuardianPro é uma plataforma web inovadora projetada para modernizar a telemedicina, focando na comunicação eficiente entre profissionais de saúde e pacientes através de um sistema de **chat interativo**. Para além da consulta remota, o GuardianPro integra **inteligência artificial** para auxiliar na **geração de laudos e resumos de atendimento**, otimizando o tempo dos médicos e melhorando a qualidade da documentação. O sistema também visa oferecer funcionalidades para gerenciamento seguro de documentos e um fluxo de trabalho intuitivo.

---

## Funcionalidades Principais (em Desenvolvimento e Implementadas)

- **Chamadas de Vídeo:** Suporte para consultas por vídeo com múltiplos usuários e armazenamento de metadados.
- **Assistência por IA para Laudos e Resumos:**
    - Transcrição de áudio de consultas (via OpenAI Whisper).
    - Geração de rascunhos de laudos/resumos de atendimento a partir de transcrições ou interações de chat (via OpenAI GPT).
    - Interface para revisão e edição médica dos documentos gerados.
- **Gerenciamento de Documentos:** Upload, listagem e download seguro de documentos médicos.
- **Sistema de Autenticação e Autorização:** Login e registro para pacientes e médicos com diferentes níveis de acesso (temporariamente simplificado para facilitar testes de funcionalidades principais).

---

## Tecnologias Utilizadas

- **Back-end:** Python, Django
- **Front-end:** HTML, CSS, JavaScript
- **Banco de Dados:** SQLite
- **Comunicação em Tempo Real & Gravação:** Agora.io
- **Inteligência Artificial:** OpenAI (API Whisper e GPT)
- **Armazenamento em Nuvem (para gravações):** AWS S3
- **Controle de Versão:** Git e GitHub

---

## Como Executar Localmente

> Requisitos: Python 3.10+ e Git

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/rflMandell/GuardianPro
    cd GuardianPro
    ```

2.  **Crie e ative o ambiente virtual:**
    *   Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   Linux/macOS:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente:**
    *   Crie um arquivo `.env` na raiz do projeto (ao lado de `manage.py`).
    *   Adicione suas chaves de API para Agora.io, OpenAI, e credenciais AWS S3 conforme necessário. Consulte a seção de configuração do projeto ou um arquivo `.env.example` (se disponível) para as variáveis necessárias. Exemplo básico:
        ```env
        # Agora.io
        AGORA_APP_ID="SUA_AGORA_APP_ID"
        AGORA_APP_CERTIFICATE="SEU_AGORA_APP_CERTIFICATE"
        # AGORA_CUSTOMER_ID="SEU_AGORA_CUSTOMER_ID" # Para API REST de gravação
        # AGORA_CUSTOMER_CERTIFICATE="SEU_AGORA_CUSTOMER_SECRET" # Para API REST de gravação

        # OpenAI
        OPENAI_API_KEY="SUA_OPENAI_API_KEY"

        # AWS S3 (se usando para gravações da Agora)
        # AWS_S3_BUCKET_NAME="seu_bucket_s3"
        # AWS_ACCESS_KEY_ID="sua_chave_de_acesso_aws"
        # AWS_SECRET_ACCESS_KEY="sua_chave_secreta_aws"
        # AWS_S3_REGION_NAME="sua_regiao_s3"
        ```

5.  **Aplique as migrações:**
    ```bash
    python manage.py migrate
    ```

6.  **Inicie o servidor local:**
    ```bash
    python manage.py runserver
    ```
    Acesse em `http://127.0.0.1:8000/`

---

## Autores

Desenvolvido por:
- Rafael Mandel
- Luis Felipe Crivellaro
- Felipe Lima

Estudantes de Engenharia de Software com foco em soluções digitais inovadoras para a área da saúde.

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
