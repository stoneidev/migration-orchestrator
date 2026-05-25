package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberEntity;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface AmbassadorMemberMapper {
    AmbassadorMember toDomain(AmbassadorMemberEntity entity);
    AmbassadorMemberEntity toEntity(AmbassadorMember domain);
}
