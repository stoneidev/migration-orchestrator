package com.silicon2.admin.shop.mp_profile.adapter.out.persistence;

import com.silicon2.admin.shop.mp_profile.adapter.out.persistence.entity.BeautyProfileEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface BeautyProfileJpaRepository extends JpaRepository<BeautyProfileEntity, Long> {
    Optional<BeautyProfileEntity> findByUserId(String userId);
}
