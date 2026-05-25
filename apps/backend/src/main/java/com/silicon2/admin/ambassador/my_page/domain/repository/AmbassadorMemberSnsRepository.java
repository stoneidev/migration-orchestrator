package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;

import java.util.List;
import java.util.Optional;

public interface AmbassadorMemberSnsRepository {
    List<AmbassadorMemberSns> findByAmbassadorMemberId(Long ambassadorMemberId);
    Optional<AmbassadorMemberSns> findById(Long id);
    AmbassadorMemberSns save(AmbassadorMemberSns sns);
}
