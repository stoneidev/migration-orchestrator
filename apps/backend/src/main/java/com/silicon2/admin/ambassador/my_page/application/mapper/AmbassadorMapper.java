package com.silicon2.admin.ambassador.my_page.application.mapper;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.ReviewSubmitResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.model.Review;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import java.util.List;

@Mapper(componentModel = "spring")
public interface AmbassadorMapper {

    @Mapping(target = "ambassadorId", source = "id")
    @Mapping(target = "hasAffiliate", ignore = true)
    @Mapping(target = "snsAccounts", ignore = true)
    AmbassadorStatusResponse toStatusResponse(AmbassadorMember member);

    @Mapping(target = "reviewId", source = "id")
    @Mapping(target = "submittedAt", source = "createdAt")
    ReviewSubmitResponse toReviewSubmitResponse(Review review);

    @Mapping(target = "id", source = "id")
    @Mapping(target = "accountId", source = "snsAccountId")
    @Mapping(target = "accountUrl", source = "snsAccountUrl")
    AmbassadorStatusResponse.SnsAccountDto toSnsAccountDto(AmbassadorMemberSns sns);

    List<AmbassadorStatusResponse.SnsAccountDto> toSnsAccountDtoList(List<AmbassadorMemberSns> snsList);
}
