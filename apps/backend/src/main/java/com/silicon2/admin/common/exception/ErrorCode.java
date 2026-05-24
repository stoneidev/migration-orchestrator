package com.silicon2.admin.common.exception;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ErrorCode {
    // Common
    INVALID_INPUT_VALUE("C001", "Invalid input value"),
    METHOD_NOT_ALLOWED("C002", "Method not allowed"),
    INTERNAL_SERVER_ERROR("C003", "Internal server error"),
    INVALID_TYPE_VALUE("C004", "Invalid type value"),
    ENTITY_NOT_FOUND("C005", "Entity not found"),
    ACCESS_DENIED("C006", "Access denied"),

    // Business
    BUSINESS_EXCEPTION("B001", "Business logic error"),
    DUPLICATE_RESOURCE("B002", "Duplicate resource"),
    RESOURCE_NOT_FOUND("B003", "Resource not found"),

    // Authentication & Authorization
    UNAUTHORIZED("A001", "Unauthorized"),
    FORBIDDEN("A002", "Forbidden"),
    INVALID_TOKEN("A003", "Invalid token"),
    EXPIRED_TOKEN("A004", "Expired token");

    private final String code;
    private final String message;
}
