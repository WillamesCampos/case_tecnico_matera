# Changelog

## [Unreleased]

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