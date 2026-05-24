package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AffiliateMemberEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AffiliateMemberJpaRepository extends JpaRepository<AffiliateMemberEntity, Long> {
    Optional<AffiliateMemberEntity> findByMemberId(Long memberId);
}
