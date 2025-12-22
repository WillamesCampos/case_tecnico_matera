# Changelog

## [Unreleased]

## [0.6.1] - API Documentation (drf-spectacular)

### Added
- **API Documentation**: Enhanced OpenAPI/Swagger documentation with drf-spectacular
- **View Documentation**: Added `extend_schema_view` decorators to all ViewSets with detailed descriptions
- **Field Documentation**: Added `help_text` to serializer fields for better API documentation
- **API Tags**: Organized endpoints by tags (Authentication, Loans, Payments, Health)
- **Security Schema**: Configured JWT Bearer authentication in OpenAPI schema

### Changed
- **SPECTACULAR_SETTINGS**: Enhanced configuration with detailed API description, tags, and UI settings
- **HealthCheckView**: Added OpenAPI schema documentation
- **LoanViewSet**: Documented all actions (list, create, retrieve, update, partial_update, destroy)
- **PaymentViewSet**: Documented all actions with validation rules and business logic descriptions

## [0.6.0] - Docker & PostgreSQL Configuration

### Added
- **Dockerfile**: Containerização da aplicação Django
- **docker-compose.yaml**: Orquestração com PostgreSQL e Django
- **Database configuration**: Suporte a PostgreSQL via variáveis de ambiente
- **Environment variables**: Configuração de banco de dados no `.env_example`
- **psycopg2-binary**: Driver PostgreSQL adicionado às dependências
- **.dockerignore**: Arquivos ignorados no build do Docker

### Changed
- `settings.py`: DATABASES agora usa PostgreSQL quando `POSTGRES_HOST` está definido, fallback para SQLite
- `.env_example`: Adicionadas variáveis de ambiente do PostgreSQL (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT)

## [0.5.0] - Step 4 - IOF (Imposto sobre Operações Financeiras) Implementation

### Added
- **IOFCalculatorService**: Calculates IOF (fixed rate 0.38% + daily rate 0.0082% per day, capped at 3% per year)
- **IOF integration**: IOF included in outstanding balance calculation
- **IOF field**: Added `iof` field to `LoanSerializer` (retrieve only)
- **IOF tests**: Comprehensive test coverage for IOF calculation service

### Changed
- `OutstandingBalanceCalculatorService`: Now includes IOF in balance calculation
- Outstanding balance formula: `(Principal + Interest + IOF) - Total Paid`
- Updated existing tests to account for IOF in calculations

## [0.4.0] - Step 3 - Business Rules & Comprehensive Testing

### Added
- **Business Rules Layer**
  - `InterestCalculatorService`: Calculates compound interest (juros compostos)
  - `PaymentAggregatorService`: Aggregates payment amounts (optimized with aggregate queries)
  - `OutstandingBalanceCalculatorService`: Calculates saldo devedor (principal + interest - payments)
  - `PaymentValidatorService`: Validates payment business rules (date, value, outstanding balance)
  - `CalculateLoanOutstandingBalanceUseCase`: Orchestrates outstanding balance calculation
  - `ValidatePaymentUseCase`: Orchestrates payment validation

- **Outstanding Balance Calculation**
  - Compound interest calculation (monthly rate)
  - Automatic calculation of months between dates using `relativedelta`
  - Integration in `LoanSerializer` (retrieve only, not in list for performance)
  - Returns `total_paid` and `remaining_balance` fields

- **Payment Validation**
  - Validates payment date >= loan request date
  - Validates payment date <= today (no future payments)
  - Validates payment value > 0
  - Validates payment value <= outstanding balance
  - Validates loan ownership

- **Data Protection**
  - Critical loan fields (`amount`, `interest_rate`, `owner`, `bank`) become read-only after payments exist
  - Prevents data inconsistency in financial calculations

- **Comprehensive Testing**
  - Model constraint tests (`test_models.py`): Database-level validations
  - Serializer tests (`test_serializers.py`): Field validation and serialization
  - Service tests: Isolated business rule tests for each service
  - Use case tests: Integration tests for use cases
  - Extended view tests: 22+ integration tests covering all scenarios (validations, isolation, edge cases)
  - Test coverage: Models, serializers, services, use cases, and views

- **Dependencies**
  - `python-dateutil`: For date calculations (`relativedelta`)
  - `freezegun`: For time control in tests

### Changed
- `LoanSerializer`: Added dynamic `read_only` fields management for critical fields
- `PaymentSerializer`: Enhanced validation to handle update scenarios correctly
- `OutstandingBalanceCalculatorService`: Now calculates months using `relativedelta` for accuracy
- Test structure: Refactored to follow AAA pattern, one scenario per test

### Fixed
- Payment value validation now happens at serializer level (prevents IntegrityError)
- Update payment validation now correctly uses instance values when not provided in request
- Decimal precision issues in compound interest tests

## [0.3.0] - Step 2 - Domain Models & API Implementation

### Added
- **Loan Model** (`apps/loans/models.py`)
  - All required fields: uuid, owner, bank, amount, interest_rate, request_date, request_ip
  - Database indexes for query optimization (owner+date patterns)
  - Database constraints: amount > 0, interest_rate 0-100%
  - Inherits from BaseModel (UUID PK, audit fields)

- **Payment Model** (`apps/payments/models.py`)
  - All required fields: uuid, loan (FK), payment_date, payment_value
  - Database indexes for query optimization (loan+date patterns)
  - Database constraint: payment_value > 0
  - Inherits from BaseModel (UUID PK, audit fields)

- **Loan Serializers** (`apps/loans/serializers.py`)
  - `LoanSerializer`: create/update with validations
  - `LoanListSerializer`: list with nested owner info
  - Auto-capture `owner` from request user (HiddenField)
  - Auto-capture `request_ip` from request
  - Calculated fields: `total_paid`, `remaining_balance` (placeholder for now)
  - Validations: amount > 0, interest_rate > 0

- **Payment Serializers** (`apps/payments/serializers.py`)
  - `PaymentSerializer`: create/update with validations
  - `PaymentListSerializer`: simplified for nested display
  - Audit fields via AuditSerializerMixin

- **Loan ViewSet** (`apps/loans/views.py`)
  - Full CRUD operations (create, list, retrieve, update, delete)
  - User isolation: `get_queryset()` filters by `owner=request.user`
  - Different serializers for list vs detail actions

- **Payment ViewSet** (`apps/payments/views.py`)
  - Full CRUD operations (create, list, retrieve, update, delete)
  - User isolation: `get_queryset()` filters by `loan__owner=request.user`

- **Test Factories** (`apps/core/tests/factories/`)
  - `UserFactory`: creates test users with faker data
  - `LoanFactory`: creates test loans with realistic data
  - `PaymentFactory`: creates test payments linked to loans
  - All using factory-boy and faker for realistic test data

- **CRUD Tests** (`apps/loans/tests/test_views.py`, `apps/payments/tests/test_views.py`)
  - Loan CRUD tests: create, list, retrieve, update, delete (5 tests)
  - Payment CRUD tests: create, list, retrieve, update, delete (5 tests)
  - User isolation tests (users can't see others' data)
  - Test coverage: 88-96%

- **URL Routing**
  - `/api/v1/loans/` - Loan endpoints
  - `/api/v1/payments/` - Payment endpoints

## [0.2.0] - Step 2 - Domain Models

### Added
- `Loan` model with required fields and database constraints
- `Payment` model with foreign key to Loan
- Database indexes for query optimization
- Database constraints for data integrity (amount, interest_rate, payment_value validations)
- Initial migrations
- Test factories (UserFactory, LoanFactory, PaymentFactory)

## [0.1.0] - Step 1 - Foundation Setup

### Added
- Django + DRF project setup
- JWT authentication
- API versioning (`/api/v1/`)
- Health check endpoint
- OpenAPI schema (drf-spectacular)
- Audit abstract model (`BaseModel`)
- Test infrastructure (pytest)
- Development tooling (ruff, black, factory-boy)
- Makefile - Commands

## [0.0.0] - Initial Project Setup