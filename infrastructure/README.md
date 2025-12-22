# Docker Setup

Este diretório contém os arquivos de configuração Docker para a aplicação Credit Track.

## Arquivos

- **Dockerfile**: Imagem Docker da aplicação Django
- **docker-compose.yaml**: Orquestração dos serviços (Django + PostgreSQL)

## Como usar

### Pré-requisitos

- Docker e Docker Compose instalados
- Arquivo `.env` configurado na raiz do projeto (copie de `.env_example`)

### Comandos

**Iniciar os containers:**
```bash
cd infrastructure
docker-compose up -d
```

**Parar os containers:**
```bash
docker-compose down
```

**Ver logs:**
```bash
docker-compose logs -f
```

**Executar migrações:**
```bash
docker-compose exec web python manage.py migrate
```

**Criar superusuário:**
```bash
docker-compose exec web python manage.py createsuperuser
```

**Acessar o shell do Django:**
```bash
docker-compose exec web python manage.py shell
```

## Serviços

- **web**: Aplicação Django (porta 8000)
- **db**: PostgreSQL (porta 5432)

## Variáveis de Ambiente

Configure no arquivo `.env` na raiz do projeto:

```env
POSTGRES_DB=credit_track_db
POSTGRES_USER=credit_track_user
POSTGRES_PASSWORD=credit_track_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

