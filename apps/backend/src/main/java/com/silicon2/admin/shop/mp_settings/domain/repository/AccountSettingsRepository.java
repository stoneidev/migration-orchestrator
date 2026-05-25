package com.silicon2.admin.shop.mp_settings.domain.repository;

import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;

import java.util.Optional;

public interface AccountSettingsRepository {
    Optional<AccountSettings> findByMemberId(Long memberId);
    AccountSettings save(AccountSettings accountSettings);
    void deleteByMemberId(Long memberId);
    boolean existsByEmail(String email);
}
