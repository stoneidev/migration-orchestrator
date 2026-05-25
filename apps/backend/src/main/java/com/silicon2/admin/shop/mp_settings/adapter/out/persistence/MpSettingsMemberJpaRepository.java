package com.silicon2.admin.shop.mp_settings.adapter.out.persistence;

import com.silicon2.admin.shop.mp_settings.adapter.out.persistence.entity.MemberEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MpSettingsMemberJpaRepository extends JpaRepository<MemberEntity, Long> {
    Optional<MemberEntity> findByMemberId(Long memberId);
    boolean existsByEmail(String email);
}
