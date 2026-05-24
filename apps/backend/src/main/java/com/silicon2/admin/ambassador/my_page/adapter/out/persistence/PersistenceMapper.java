package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.domain.model.*;
import org.mapstruct.Mapper;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Mapper(componentModel = "spring")
public interface PersistenceMapper {

    AmbassadorMember toDomain(AmbassadorMemberEntity entity);
    AmbassadorMemberEntity toEntity(AmbassadorMember domain);

    AmbassadorMemberSns toDomain(AmbassadorMemberSnsEntity entity);
    AmbassadorMemberSnsEntity toEntity(AmbassadorMemberSns domain);

    Campaign toDomain(CampaignEntity entity);
    CampaignEntity toEntity(Campaign domain);

    AffiliateMember toDomain(AffiliateMemberEntity entity);
    AffiliateMemberEntity toEntity(AffiliateMember domain);

    default Review toDomain(ReviewEntity entity) {
        if (entity == null) return null;
        return Review.builder()
                .id(entity.getId())
                .campaignId(entity.getCampaignId())
                .ambassadorMemberId(entity.getAmbassadorMemberId())
                .content(entity.getContent())
                .rating(entity.getRating())
                .imageUrls(entity.getImageUrls() != null && !entity.getImageUrls().isEmpty()
                        ? Arrays.asList(entity.getImageUrls().split(","))
                        : null)
                .status(entity.getStatus())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
    }

    default ReviewEntity toEntity(Review domain) {
        if (domain == null) return null;
        return ReviewEntity.builder()
                .id(domain.getId())
                .campaignId(domain.getCampaignId())
                .ambassadorMemberId(domain.getAmbassadorMemberId())
                .content(domain.getContent())
                .rating(domain.getRating())
                .imageUrls(domain.getImageUrls() != null && !domain.getImageUrls().isEmpty()
                        ? String.join(",", domain.getImageUrls())
                        : null)
                .status(domain.getStatus())
                .createdAt(domain.getCreatedAt())
                .updatedAt(domain.getUpdatedAt())
                .build();
    }

    List<AmbassadorMemberSns> toDomainList(List<AmbassadorMemberSnsEntity> entities);
}
