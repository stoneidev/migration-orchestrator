package com.silicon2.admin.shop.mp_question.adapter.out.persistence.mapper;

import com.silicon2.admin.shop.mp_question.adapter.out.persistence.entity.QuestionEntity;
import com.silicon2.admin.shop.mp_question.domain.model.Question;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface QuestionMapper {
    Question toDomain(QuestionEntity entity);

    QuestionEntity toEntity(Question domain);
}
