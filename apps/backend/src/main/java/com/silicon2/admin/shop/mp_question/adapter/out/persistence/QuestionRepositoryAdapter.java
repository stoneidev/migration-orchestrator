package com.silicon2.admin.shop.mp_question.adapter.out.persistence;

import com.silicon2.admin.shop.mp_question.adapter.out.persistence.mapper.QuestionMapper;
import com.silicon2.admin.shop.mp_question.domain.model.Question;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
@RequiredArgsConstructor
public class QuestionRepositoryAdapter implements QuestionRepository {

    private final QuestionJpaRepository jpaRepository;
    private final QuestionMapper mapper;

    @Override
    public List<Question> findAll() {
        return jpaRepository.findAll().stream().map(mapper::toDomain).toList();
    }

    @Override
    public List<Question> findByUserId(String userId) {
        return jpaRepository.findByUserId(userId).stream().map(mapper::toDomain).toList();
    }

    @Override
    public Question save(Question question) {
        return mapper.toDomain(jpaRepository.save(mapper.toEntity(question)));
    }

    @Override
    public void deleteById(Long questionId) {
        jpaRepository.deleteById(questionId);
    }

    @Override
    public long count() {
        return jpaRepository.count();
    }
}
