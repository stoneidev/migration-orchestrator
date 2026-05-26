package com.silicon2.admin.shop.mp_question.adapter.out.persistence;

import com.silicon2.admin.shop.mp_question.adapter.out.persistence.entity.QuestionEntity;
import com.silicon2.admin.shop.mp_question.domain.model.QuestionStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface QuestionJpaRepository extends JpaRepository<QuestionEntity, Long> {
    List<QuestionEntity> findByUserId(String userId);

    List<QuestionEntity> findByStatus(QuestionStatus status);
}
