# Changelog

## [Unreleased]

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