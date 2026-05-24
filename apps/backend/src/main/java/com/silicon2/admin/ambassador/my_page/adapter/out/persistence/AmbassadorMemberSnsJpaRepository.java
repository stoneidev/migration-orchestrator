package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AmbassadorMemberSnsJpaRepository extends JpaRepository<AmbassadorMemberSnsEntity, Long> {
    List<AmbassadorMemberSnsEntity> findByAmbassadorMemberId(Long ambassadorMemberId);
}
