package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AmbassadorMemberJpaRepository extends JpaRepository<AmbassadorMemberEntity, Long> {
    Optional<AmbassadorMemberEntity> findByMemberId(Long memberId);
}
