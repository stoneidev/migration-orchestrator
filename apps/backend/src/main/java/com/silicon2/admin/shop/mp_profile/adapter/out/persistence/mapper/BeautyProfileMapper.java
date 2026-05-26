package com.silicon2.admin.shop.mp_profile.adapter.out.persistence.mapper;

import com.silicon2.admin.shop.mp_profile.adapter.out.persistence.entity.BeautyProfileEntity;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface BeautyProfileMapper {
    BeautyProfile toDomain(BeautyProfileEntity entity);

    BeautyProfileEntity toEntity(BeautyProfile domain);
}
