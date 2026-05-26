package com.silicon2.admin.shop.mp_profile.domain.repository;

import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;

import java.util.Optional;

public interface BeautyProfileRepository {
    Optional<BeautyProfile> findByUserId(String userId);

    BeautyProfile save(BeautyProfile profile);

    long count();
}
