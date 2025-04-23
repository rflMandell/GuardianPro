# GuardianPro
**Plataforma SaaS de Telemedicina com Assistência por IA**  
🚧 *Projeto em desenvolvimento ativo*

GuardianPro é uma plataforma web voltada para clínicas e profissionais de saúde, oferecendo uma solução completa para telemedicina. O sistema inclui chamadas de vídeo, armazenamento seguro de documentos médicos, e interface simples de navegação — tudo com foco na eficiência e segurança do atendimento médico.

---

## Funcionalidades Concluídas

- ✅ Chamadas de vídeo com múltiplos usuários e armazenamento de seus metadados
- ✅ Upload, listagem e download de documentos
- ⏳ Sistema de login e registro (desativado temporariamente)
- ⏳ Assistência por IA na criação de laudos médicos
- ⏳ Gerenciamento de pacientes e médicos com permissões específicas

---

## Tecnologias Utilizadas

- **Back-end:** Python, Django
- **Front-end:** HTML, CSS, JavaScript
- **Banco de Dados:** SQLite
- **Serviços Externos:** Agora.io
- **Controle de Versão:** Git e GitHub

---

## Como Executar Localmente

> Requisitos: Python 3.10+ e Git

```bash
# Clone o repositório
git clone https://github.com/rflMandell/GuardianPro
cd GuardianPro

# Crie e ative o ambiente virtual
python -m venv venv
source venv\Scripts\activate no Windows

# Instale as dependências
pip install -r requirements.txt

# Aplique as migrações
python manage.py migrate

# Inicie o servidor local
python manage.py runserver
```

# Autor
Desenvolvido por Rafael Mandel – estudante de Engenharia de Software com foco em soluções digitais para saúde.

# Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.