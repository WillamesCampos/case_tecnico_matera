<div align="center">
  <img width="250" height="250" alt="Credit Track Logo" src="https://github.com/user-attachments/assets/235eeaf6-a4d0-4bc0-97a3-4e2cbcfe1380" />
</div>



# Credit Track API

API REST desenvolvida com Django e Django REST Framework para gerenciamento de empréstimos e pagamentos, com cálculo automático de saldo devedor considerando juros compostos e IOF.

## 📋 Objetivo

O Credit Track é uma API que permite aos usuários:

- Gerenciar seus empréstimos (criar, listar, visualizar, atualizar e excluir)
- Registrar pagamentos realizados
- Visualizar o saldo devedor atualizado de cada empréstimo
- Calcular automaticamente juros compostos mensais e IOF (Imposto sobre Operações Financeiras)

A API garante isolamento de dados, onde cada usuário pode acessar apenas seus próprios empréstimos e pagamentos, utilizando autenticação via JWT (JSON Web Tokens).

## 🚀 Instalação

### Pré-requisitos

- Python 3.12 ou superior
- Poetry (gerenciador de dependências)

### Passos de Instalação

1. **Clone o repositório** (se aplicável)

2. **Instale as dependências usando Poetry:**
   ```bash
   poetry install
   ```

3. **Ative o ambiente virtual:**
   ```bash
   poetry shell
   ```

4. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```env
   DJANGO_SECRET_KEY=sua-chave-secreta-aqui
   ENVIRONMENT=dev
   ```

5. **Execute as migrações:**
   ```bash
   make migrate
   ```

6. **Crie um superusuário (opcional, para acesso ao admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Execute o servidor de desenvolvimento:**
   ```bash
   make run
   ```

A API estará disponível em `http://localhost:8000`

## 📁 Estrutura do Projeto

```
credit-track/
├── apps/                    # Aplicações Django
│   ├── core/               # App core (User, BaseModel, utilitários)
│   │   ├── models.py       # Modelo User customizado
│   │   ├── serializers/    # Serializers base e mixins
│   │   ├── services/       # Serviços base
│   │   ├── use_cases/      # Use cases base
│   │   └── tests/          # Testes e factories
│   ├── loans/              # App de empréstimos
│   │   ├── models.py       # Modelo Loan
│   │   ├── serializers.py  # Serializers de Loan
│   │   ├── views.py        # ViewSet de Loan
│   │   ├── services/       # Serviços de negócio
│   │   │   ├── interest_calculator_svc.py
│   │   │   ├── iof_calculator_svc.py
│   │   │   ├── outstanding_balance_calculator_svc.py
│   │   │   ├── payment_aggregator_svc.py
│   │   │   └── payment_validator_svc.py
│   │   ├── use_cases/      # Casos de uso
│   │   └── tests/          # Testes unitários e de integração
│   └── payments/           # App de pagamentos
│       ├── models.py       # Modelo Payment
│       ├── serializers.py  # Serializers de Payment
│       ├── views.py        # ViewSet de Payment
│       └── tests/          # Testes
├── credit_track/           # Configurações do projeto Django
│   ├── settings.py         # Configurações principais
│   ├── test_settings.py    # Configurações para testes
│   └── urls.py             # URLs principais
├── infrastructure/         # Docker e configurações de infraestrutura
├── CHANGELOG.md            # Histórico de mudanças
├── DEVELOPER_NOTES.md      # Notas técnicas e decisões de design
├── IOF_CALCULATION_RULES.md # Regras de cálculo do IOF
├── Makefile                # Comandos automatizados
├── manage.py               # Script de gerenciamento Django
└── pyproject.toml          # Configuração do projeto e dependências
```

## 🛠️ Comandos Makefile

### Django

- `make migrations` - Cria migrações do banco de dados
- `make showmigrations` - Lista o status das migrações
- `make migrate` - Aplica as migrações
- `make run` - Inicia o servidor de desenvolvimento
- `make shell` - Abre o shell interativo do Django

### Linting e Formatação

- `make format` - Formata o código com ruff
- `make check` - Verifica o código com ruff (sem corrigir)
- `make fix` - Corrige automaticamente problemas encontrados pelo ruff
- `make lint` - Executa formatação, verificação e correção

### Testes

- `make test` - Executa todos os testes com pytest e gera relatório de cobertura

## 📚 Documentação da API

### Endpoints Disponíveis

A API está disponível em `/api/v1/`:

- **Autenticação:**
  - `POST /api/v1/auth/token/` - Obter token JWT
  - `POST /api/v1/auth/token/refresh/` - Renovar token JWT

- **Empréstimos:**
  - `GET /api/v1/loans/` - Listar empréstimos do usuário
  - `POST /api/v1/loans/` - Criar novo empréstimo
  - `GET /api/v1/loans/{uuid}/` - Detalhes do empréstimo (inclui saldo devedor e IOF)
  - `PATCH /api/v1/loans/{uuid}/` - Atualizar empréstimo
  - `DELETE /api/v1/loans/{uuid}/` - Excluir empréstimo

- **Pagamentos:**
  - `GET /api/v1/payments/` - Listar pagamentos do usuário
  - `POST /api/v1/payments/` - Criar novo pagamento
  - `GET /api/v1/payments/{uuid}/` - Detalhes do pagamento
  - `PATCH /api/v1/payments/{uuid}/` - Atualizar pagamento
  - `DELETE /api/v1/payments/{uuid}/` - Excluir pagamento

- **Documentação Interativa:**
  - `GET /api/v1/swagger-ui/` - Interface Swagger UI
  - `GET /api/v1/redoc/` - Documentação ReDoc
  - `GET /api/v1/schema/` - Schema OpenAPI

### Autenticação

A API utiliza autenticação JWT. Para acessar os endpoints protegidos:

1. Obtenha um token fazendo POST em `/api/v1/auth/token/` com `username` e `password`
2. Inclua o token no header: `Authorization: Bearer {token}`

### Exemplo de Uso

```bash
# Obter token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "senha"}'

# Criar empréstimo
curl -X POST http://localhost:8000/api/v1/loans/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "bank": "Banco Exemplo",
    "amount": 10000.00,
    "interest_rate": 2.5,
    "request_date": "2024-01-01"
  }'

# Visualizar empréstimo (inclui saldo devedor e IOF)
curl -X GET http://localhost:8000/api/v1/loans/{uuid}/ \
  -H "Authorization: Bearer {token}"
```

## 🧪 Testes

O projeto utiliza `pytest` e `pytest-django` para testes. A cobertura de código é mantida acima de 75%.

### Executar Testes

```bash
make test
```

### Estrutura de Testes

- **Testes de Modelos** (`test_models.py`): Validações de constraints do banco de dados
- **Testes de Serializers** (`test_serializers.py`): Validação de campos e serialização
- **Testes de Serviços**: Regras de negócio isoladas (cálculos, validações)
- **Testes de Use Cases**: Orquestração de serviços
- **Testes de Views** (`test_views.py`): Testes de integração (CRUD, isolamento, validações)

## 📊 Funcionalidades Principais

### Cálculo de Saldo Devedor

O saldo devedor é calculado dinamicamente usando a fórmula:

```
Saldo Devedor = (Principal + Juros Compostos + IOF) - Total Pago
```

- **Juros Compostos**: Calculados mensalmente sobre o valor principal
- **IOF**: Imposto sobre Operações Financeiras (0,38% fixo + 0,0082% ao dia, limitado a 3% ao ano)
- **Total Pago**: Soma de todos os pagamentos realizados

### Validações de Negócio

- Pagamentos não podem exceder o saldo devedor
- Pagamentos não podem ser feitos antes da data de solicitação do empréstimo
- Pagamentos não podem ser feitos com data futura
- Campos críticos do empréstimo ficam bloqueados após a criação de pagamentos

### Isolamento de Dados

Cada usuário pode acessar apenas seus próprios empréstimos e pagamentos. A filtragem é feita automaticamente nos ViewSets.

## 📝 Documentação Adicional

- **[CHANGELOG.md](CHANGELOG.md)**: Histórico completo de mudanças e versões
- **[DEVELOPER_NOTES.md](DEVELOPER_NOTES.md)**: Decisões técnicas e arquiteturais
- **[IOF_CALCULATION_RULES.md](IOF_CALCULATION_RULES.md)**: Regras detalhadas de cálculo do IOF

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas:

- **Models**: Entidades do domínio (Loan, Payment, User)
- **Serializers**: Validação e serialização de dados
- **Views**: Endpoints da API (ViewSets)
- **Services**: Lógica de negócio reutilizável
- **Use Cases**: Orquestração de serviços para casos de uso específicos

## 🔒 Segurança

- Autenticação via JWT (JSON Web Tokens)
- Isolamento de dados por usuário
- Validações de negócio em múltiplas camadas
- Proteção de campos críticos após operações financeiras

## 📦 Tecnologias Utilizadas

- **Django 6.0**: Framework web
- **Django REST Framework**: Construção da API REST
- **djangorestframework-simplejwt**: Autenticação JWT
- **drf-spectacular**: Documentação OpenAPI/Swagger
- **pytest**: Framework de testes
- **factory-boy**: Criação de dados de teste
- **ruff**: Linter e formatter
- **python-dateutil**: Cálculos de datas
- **freezegun**: Controle de tempo em testes

## 📄 Licença

Este projeto foi desenvolvido como case técnico.

## 👤 Autor

**Willames Campos**
- Email: willwjccampos@gmail.com

