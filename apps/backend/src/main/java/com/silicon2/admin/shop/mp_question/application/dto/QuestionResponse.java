package com.silicon2.admin.shop.mp_question.application.dto;

import com.silicon2.admin.shop.mp_question.domain.Question;
import com.silicon2.admin.shop.mp_question.domain.QuestionStatus;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class QuestionResponse {
    private Long id;
    private String productName;
    private String category;
    private String questionText;
    private String answerText;
    private String userId;
    private String userName;
    private LocalDateTime createdAt;
    private QuestionStatus status;

    public static QuestionResponse from(Question question) {
        return new QuestionResponse(
            question.getId(),
            question.getProductName(),
            question.getCategory(),
            question.getQuestionText(),
            question.getAnswerText(),
            question.getUserId(),
            question.getUserName(),
            question.getCreatedAt(),
            question.getStatus()
        );
    }
}
