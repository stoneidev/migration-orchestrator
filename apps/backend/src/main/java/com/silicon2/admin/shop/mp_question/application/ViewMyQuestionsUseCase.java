package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ViewMyQuestionsUseCase {

    private final QuestionRepository questionRepository;

    @Transactional(readOnly = true)
    public List<QuestionResponse> execute(String userId) {
        return questionRepository.findByUserId(userId).stream()
            .map(QuestionResponse::from)
            .collect(Collectors.toList());
    }
}
