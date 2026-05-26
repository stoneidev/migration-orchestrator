package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class DeleteQuestionUseCase {

    private final QuestionRepository questionRepository;

    @Transactional
    public void execute(Long questionId) {
        questionRepository.deleteById(questionId);
    }
}
