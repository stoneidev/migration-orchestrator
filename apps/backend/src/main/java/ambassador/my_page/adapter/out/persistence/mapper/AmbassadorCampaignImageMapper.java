package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorCampaignImageEntity;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorCampaignImage;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface AmbassadorCampaignImageMapper {
    AmbassadorCampaignImage toDomain(AmbassadorCampaignImageEntity entity);
    AmbassadorCampaignImageEntity toEntity(AmbassadorCampaignImage domain);
}
