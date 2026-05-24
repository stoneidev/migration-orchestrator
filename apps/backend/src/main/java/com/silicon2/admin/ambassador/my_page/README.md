# Ambassador My Page - DDD/Hexagonal Architecture

## Overview
Feature ID: `ambassador.my_page`  
Module: Ambassador  
Architecture: DDD + Hexagonal (Clean Architecture)

## Business Rules Implemented
- **BR-001**: Access control - Only active ambassadors can access
- **BR-002**: Review submission during campaign active period only
- **BR-003**: One review per campaign per ambassador
- **BR-004**: Unique tracking code generation for SNS links
- **BR-005**: Shipping info visibility (to be implemented)
- **BR-006**: Affiliate member validation for commission eligibility
- **BR-007**: Maximum 5 images per review
- **BR-008**: At least one SNS account required for link generation

## Package Structure

```
ambassador.my_page/
├── domain/
│   ├── model/                          # Domain entities (pure business logic)
│   │   ├── AmbassadorMember.java
│   │   ├── AmbassadorMemberSns.java
│   │   ├── AffiliateMember.java
│   │   ├── Campaign.java
│   │   └── Review.java
│   ├── repository/                     # Repository interfaces (ports)
│   │   ├── AmbassadorMemberRepository.java
│   │   ├── AmbassadorMemberSnsRepository.java
│   │   ├── AffiliateMemberRepository.java
│   │   ├── CampaignRepository.java
│   │   └── ReviewRepository.java
│   └── service/                        # Domain services
│       └── AmbassadorDomainService.java
├── application/
│   ├── dto/                            # Request/Response DTOs
│   │   ├── AmbassadorStatusResponse.java
│   │   ├── ReviewSubmitRequest.java
│   │   ├── ReviewSubmitResponse.java
│   │   ├── SnsLinkRequest.java
│   │   └── SnsLinkResponse.java
│   ├── mapper/                         # DTO mappers
│   │   └── AmbassadorMapper.java
│   └── usecase/                        # Use cases (application services)
│       ├── CheckAmbassadorStatusUseCase.java
│       ├── SubmitReviewUseCase.java
│       └── GenerateSnsLinkUseCase.java
└── adapter/
    ├── in/
    │   └── web/                        # REST Controllers
    │       └── AmbassadorMyPageController.java
    └── out/
        └── persistence/                # JPA implementation
            ├── *Entity.java            # JPA entities
            ├── *JpaRepository.java     # Spring Data JPA interfaces
            ├── *RepositoryImpl.java    # Repository implementations
            └── PersistenceMapper.java  # Entity-Domain mappers
```

## API Endpoints

### 1. Check Ambassador Status
**GET** `/api/ambassador/my-page/status/{ambassadorId}`

Response:
```json
{
  "success": true,
  "data": {
    "ambassadorId": 1,
    "status": "ACTIVE",
    "name": "John Doe",
    "email": "john@example.com",
    "hasAffiliate": true,
    "snsAccounts": [
      {
        "id": 1,
        "snsType": "INSTAGRAM",
        "accountId": "@johndoe",
        "accountUrl": "https://instagram.com/johndoe",
        "followerCount": 10000,
        "isVerified": true
      }
    ],
    "joinedAt": "2024-01-01T00:00:00"
  }
}
```

### 2. Submit Review
**POST** `/api/ambassador/my-page/review/{ambassadorId}`

Request:
```json
{
  "campaignId": 1,
  "content": "Great product! Highly recommended.",
  "rating": 5,
  "imageUrls": [
    "https://cdn.example.com/img1.jpg",
    "https://cdn.example.com/img2.jpg"
  ]
}
```

Response:
```json
{
  "success": true,
  "data": {
    "reviewId": 123,
    "campaignId": 1,
    "status": "PENDING",
    "submittedAt": "2024-05-24T12:00:00"
  }
}
```

### 3. Generate SNS Link
**POST** `/api/ambassador/my-page/sns-link/{ambassadorId}`

Request:
```json
{
  "baseUrl": "https://shop.example.com/product/123",
  "snsType": "INSTAGRAM"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "trackingUrl": "https://shop.example.com/product/123?ref=AMB001-a1b2c3d4",
    "trackingCode": "AMB001",
    "snsType": "INSTAGRAM"
  }
}
```

## Database Schema

Tables created by migration `V001__create_ambassador_tables.sql`:
- `ambassador_member`
- `ambassador_member_sns`
- `ambassador_campaign`
- `ambassador_campaign_image`
- `ambassador_review`
- `affiliate_member`

## Technology Stack
- **Java 21**
- **Spring Boot 3.4**
- **Spring Data JPA**
- **MapStruct** (DTO mapping)
- **Lombok** (boilerplate reduction)
- **Flyway** (database migration)
- **MySQL/MariaDB**

## Design Principles Applied

### 1. DDD (Domain-Driven Design)
- Domain models contain business logic
- Domain services handle cross-entity business rules
- Rich domain models with behavior (not anemic)

### 2. Hexagonal Architecture
- **Domain Layer**: Pure business logic, no dependencies
- **Application Layer**: Use cases orchestrate domain operations
- **Adapters**: 
  - **In**: REST controllers (web)
  - **Out**: JPA repositories (persistence)

### 3. Dependency Rule
```
Adapters → Application → Domain
   ↓           ↓
  UI        Use Cases → Domain Models
Database              ← Repository Interfaces
```

Dependencies point inward. Domain has no external dependencies.

## Error Handling

All business rule violations throw exceptions:
- `BusinessException` with appropriate `ErrorCode`
- Handled by `GlobalExceptionHandler`
- Returns standardized `ApiResponse` with error details

## Testing Strategy (To Be Implemented)

1. **Domain Tests**: Pure unit tests for domain logic
2. **Use Case Tests**: Mock repositories, test business flows
3. **Integration Tests**: Test full stack with test containers
4. **API Tests**: REST API contract testing

## Future Enhancements

1. Shipping info visibility (BR-005)
2. Campaign participation history
3. Commission tracking
4. Review moderation workflow
5. SNS link analytics
6. Event-driven architecture (Domain Events)
