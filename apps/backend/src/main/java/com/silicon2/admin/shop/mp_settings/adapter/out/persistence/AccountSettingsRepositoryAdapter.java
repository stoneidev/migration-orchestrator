package com.silicon2.admin.shop.mp_settings.adapter.out.persistence;

import com.silicon2.admin.shop.mp_settings.adapter.out.persistence.entity.MemberEntity;
import com.silicon2.admin.shop.mp_settings.adapter.out.persistence.mapper.MemberMapper;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import com.silicon2.admin.shop.mp_settings.domain.repository.AccountSettingsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class AccountSettingsRepositoryAdapter implements AccountSettingsRepository {

    private final MpSettingsMemberJpaRepository memberJpaRepository;
    private final MemberMapper memberMapper;

    @Override
    public Optional<AccountSettings> findByMemberId(Long memberId) {
        return memberJpaRepository.findByMemberId(memberId)
                .map(memberMapper::toDomain);
    }

    @Override
    public AccountSettings save(AccountSettings accountSettings) {
        MemberEntity entity = memberMapper.toEntity(accountSettings);
        MemberEntity saved = memberJpaRepository.save(entity);
        return memberMapper.toDomain(saved);
    }

    @Override
    public void deleteByMemberId(Long memberId) {
        memberJpaRepository.deleteById(memberId);
    }

    @Override
    public boolean existsByEmail(String email) {
        return memberJpaRepository.existsByEmail(email);
    }
}
