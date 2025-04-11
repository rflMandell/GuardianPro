# GuardianPro
**Plataforma SaaS de Telemedicina com Assistência por IA**  
🚧 *Projeto em desenvolvimento ativo*

GuardianPro é uma plataforma web voltada para clínicas e profissionais de saúde, oferecendo uma solução completa para telemedicina. O sistema inclui chamadas de vídeo, geração automática de laudos com suporte de IA, gerenciamento de pacientes, prontuários e armazenamento em nuvem — tudo com foco na eficiência e segurança do atendimento médico.

---

## Funcionalidades (em progresso)

- ✅ Sistema de login com níveis de acesso (admin, médico, paciente)
- ✅ Chamadas de vídeo e voz com múltiplos usuários
- ⏳ Assistência por IA na criação de laudos médicos
- ⏳ Gerenciamento de pacientes, médicos e consultas
- ⏳ Armazenamento seguro de arquivos (nuvem)

---

## Tecnologias Utilizadas

- **Back-end:** Python, Django, Django REST Framework
- **Front-end:** HTML, CSS, JavaScript, Tailwind CSS
- **Futuro:** React, FastAPI (para serviços de IA)
- **Banco de Dados:** SQLite (desenvolvimento), PostgreSQL (produção)
- **Integrações:** Agora.io, OpenAI API
- **Controle de Versão:** Git e GitHub

---

## Como Executar Localmente

> Requisitos: Python 3.10+ e Git

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/guardianpro.git
cd guardianpro

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# Instale as dependências
pip install -r requirements.txt

# Aplique as migrações
python manage.py migrate

# Inicie o servidor local
python manage.py runserver
```

# Roadmap (parcial)

- ✅ Integração com Agora.io

- ✅ Geração de links de chamada

- ⏳ Integração com IA para auxílio em laudos

- ⏳ Upload de arquivos e integração com nuvem

- ⏳ Painel administrativo

- ⏳ Interface para pacientes

# Autor
Desenvolvido por Rafael Mandel – estudante de Engenharia de Software com foco em soluções digitais para saúde.

# Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.