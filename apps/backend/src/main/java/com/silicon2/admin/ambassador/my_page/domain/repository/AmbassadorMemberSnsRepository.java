package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;

import java.util.List;

public interface AmbassadorMemberSnsRepository {
    List<AmbassadorMemberSns> findByAmbassadorMemberId(Long ambassadorMemberId);
    AmbassadorMemberSns save(AmbassadorMemberSns sns);
}
