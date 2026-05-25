package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionRequest;
import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.Question;
import com.silicon2.admin.shop.mp_question.domain.QuestionRepository;
import com.silicon2.admin.shop.mp_question.domain.QuestionStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class SubmitQuestionUseCase {

    private final QuestionRepository questionRepository;

    @Transactional
    public QuestionResponse execute(QuestionRequest request) {
        Question question = new Question();
        question.setProductName(request.getProductName());
        question.setCategory(request.getCategory());
        question.setQuestionText(request.getQuestionText());
        question.setUserId(request.getUserId());
        question.setUserName(request.getUserName());
        question.setCreatedAt(LocalDateTime.now());
        question.setStatus(QuestionStatus.UNANSWERED);

        Question saved = questionRepository.save(question);
        return QuestionResponse.from(saved);
    }
}
