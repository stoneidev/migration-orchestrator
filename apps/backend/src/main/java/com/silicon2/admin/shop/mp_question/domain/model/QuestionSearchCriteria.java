package com.silicon2.admin.shop.mp_question.domain.model;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class QuestionSearchCriteria {
    private final String category;
    private final String dateFrom;
    private final String dateTo;
    private final String status;

    public boolean matches(Question question) {
        return question.matchesCategory(category)
                && question.isWithinDateRange(dateFrom, dateTo)
                && question.matchesStatus(status);
    }
}
