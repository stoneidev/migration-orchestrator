package com.silicon2.admin.shop.mp_settings.adapter.out.persistence.mapper;

import com.silicon2.admin.shop.mp_settings.adapter.out.persistence.entity.MemberEntity;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface MemberMapper {

    AccountSettings toDomain(MemberEntity entity);

    @Mapping(target = "passwordHash", constant = "")
    MemberEntity toEntity(AccountSettings domain);
}
