package com.silicon2.admin.shop.mp_profile.adapter.out.persistence.mapper;

import com.silicon2.admin.shop.mp_profile.adapter.out.persistence.entity.BeautyProfileEntity;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface BeautyProfileMapper {

    @Mapping(target = "skinConcernAsList", ignore = true)
    @Mapping(target = "healthConcernAsList", ignore = true)
    @Mapping(target = "cleanBeautyPreferencesAsList", ignore = true)
    @Mapping(target = "hairConcernAsList", ignore = true)
    BeautyProfile toDomain(BeautyProfileEntity entity);

    BeautyProfileEntity toEntity(BeautyProfile domain);
}
