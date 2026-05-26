package com.silicon2.admin.shop.mp_question.domain.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Question {
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("MM/dd/yyyy");

    private Long id;
    private String productName;
    private String category;
    private String questionText;
    private String answerText;
    private String userId;
    private String userName;
    private LocalDateTime createdAt;
    private QuestionStatus status;

    public static Question create(
            String productName,
            String category,
            String questionText,
            String userId,
            String userName
    ) {
        Question question = new Question();
        question.setProductName(productName);
        question.setCategory(category);
        question.setQuestionText(questionText);
        question.setUserId(userId);
        question.setUserName(userName);
        question.setCreatedAt(LocalDateTime.now());
        question.setStatus(QuestionStatus.UNANSWERED);
        return question;
    }

    public boolean matchesSearchCriteria(QuestionSearchCriteria criteria) {
        return criteria.matches(this);
    }

    public boolean matchesCategory(String category) {
        return category == null
                || category.isEmpty()
                || "All".equals(category)
                || this.category.equals(category);
    }

    public boolean matchesStatus(String status) {
        return status == null || status.isEmpty() || this.status.name().equals(status);
    }

    public boolean isWithinDateRange(String dateFrom, String dateTo) {
        if (dateFrom == null && dateTo == null) {
            return true;
        }

        try {
            if (dateFrom != null && !dateFrom.isEmpty()) {
                LocalDate fromDate = LocalDate.parse(dateFrom, DATE_FORMATTER);
                if (createdAt.toLocalDate().isBefore(fromDate)) {
                    return false;
                }
            }

            if (dateTo != null && !dateTo.isEmpty()) {
                LocalDate toDate = LocalDate.parse(dateTo, DATE_FORMATTER);
                if (createdAt.toLocalDate().isAfter(toDate)) {
                    return false;
                }
            }

            return true;
        } catch (Exception e) {
            return true;
        }
    }
}
