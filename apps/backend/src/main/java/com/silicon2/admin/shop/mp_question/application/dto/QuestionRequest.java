package com.silicon2.admin.shop.mp_question.application.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class QuestionRequest {
    private String productName;
    private String category;
    private String questionText;
    private String userId;
    private String userName;
}
