package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberSnsEntity;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface AmbassadorMemberSnsMapper {
    AmbassadorMemberSns toDomain(AmbassadorMemberSnsEntity entity);
    AmbassadorMemberSnsEntity toEntity(AmbassadorMemberSns domain);
}
