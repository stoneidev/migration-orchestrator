package com.silicon2.admin.common.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@NoArgsConstructor(access = AccessLevel.PRIVATE)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    private boolean success;
    private T data;
    private ErrorInfo error;
    private MetaInfo meta;
    private LocalDateTime timestamp;

    public static <T> ApiResponse<T> success() {
        return new ApiResponse<>(true, null, null, null, LocalDateTime.now());
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, null, null, LocalDateTime.now());
    }

    public static <T> ApiResponse<T> success(T data, MetaInfo meta) {
        return new ApiResponse<>(true, data, null, meta, LocalDateTime.now());
    }

    public static <T> ApiResponse<T> error(String code, String message) {
        return new ApiResponse<>(false, null, new ErrorInfo(code, message), null, LocalDateTime.now());
    }

    public static <T> ApiResponse<T> error(ErrorInfo error) {
        return new ApiResponse<>(false, null, error, null, LocalDateTime.now());
    }

    @Getter
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class ErrorInfo {
        private String code;
        private String message;
    }

    @Getter
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class MetaInfo {
        private Integer page;
        private Integer size;
        private Long totalElements;
        private Integer totalPages;
    }
}
