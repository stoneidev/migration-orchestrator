package com.silicon2.admin.shop.mp_profile.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface BeautyProfileRepository extends JpaRepository<BeautyProfile, Long> {
    Optional<BeautyProfile> findByUserId(String userId);
}
