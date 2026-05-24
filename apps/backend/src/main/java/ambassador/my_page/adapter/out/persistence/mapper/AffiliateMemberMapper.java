package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AffiliateMemberEntity;
import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface AffiliateMemberMapper {
    AffiliateMember toDomain(AffiliateMemberEntity entity);
    AffiliateMemberEntity toEntity(AffiliateMember domain);
}
