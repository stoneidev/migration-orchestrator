package com.silicon2.admin.shop.mp_question.domain.repository;

import com.silicon2.admin.shop.mp_question.domain.model.Question;

import java.util.List;

public interface QuestionRepository {
    List<Question> findAll();

    List<Question> findByUserId(String userId);

    Question save(Question question);

    void deleteById(Long questionId);

    long count();
}
