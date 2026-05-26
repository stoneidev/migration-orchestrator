package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.model.QuestionSearchCriteria;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ListQuestionsUseCase {

    private final QuestionRepository questionRepository;

    @Transactional(readOnly = true)
    public List<QuestionResponse> execute(String category, String dateFrom, String dateTo, String status) {
        QuestionSearchCriteria criteria = new QuestionSearchCriteria(category, dateFrom, dateTo, status);

        return questionRepository.findAll().stream()
                .filter(question -> question.matchesSearchCriteria(criteria))
                .map(QuestionResponse::from)
                .collect(Collectors.toList());
    }
}
