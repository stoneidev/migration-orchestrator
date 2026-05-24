package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AffiliateMemberJpaRepository extends JpaRepository<AffiliateMemberEntity, Long> {
    Optional<AffiliateMemberEntity> findByAmbassadorMemberId(Long ambassadorMemberId);
}
