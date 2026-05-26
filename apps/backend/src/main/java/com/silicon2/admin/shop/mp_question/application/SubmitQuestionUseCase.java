package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionRequest;
import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.model.Question;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class SubmitQuestionUseCase {

    private final QuestionRepository questionRepository;

    @Transactional
    public QuestionResponse execute(QuestionRequest request) {
        Question question = Question.create(
                request.getProductName(),
                request.getCategory(),
                request.getQuestionText(),
                request.getUserId(),
                request.getUserName()
        );

        return QuestionResponse.from(questionRepository.save(question));
    }
}
