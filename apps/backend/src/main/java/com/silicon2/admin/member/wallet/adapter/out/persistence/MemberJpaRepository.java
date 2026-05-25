package com.silicon2.admin.member.wallet.adapter.out.persistence;

import com.silicon2.admin.member.wallet.adapter.out.persistence.entity.MemberWalletEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface MemberJpaRepository extends JpaRepository<MemberWalletEntity, Long> {
    Optional<MemberWalletEntity> findByMbId(String mbId);
}
