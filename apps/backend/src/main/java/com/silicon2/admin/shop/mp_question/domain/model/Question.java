package com.silicon2.admin.shop.mp_question.domain.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Question {
    private Long id;
    private String productName;
    private String category;
    private String questionText;
    private String answerText;
    private String userId;
    private String userName;
    private LocalDateTime createdAt;
    private QuestionStatus status;
}
