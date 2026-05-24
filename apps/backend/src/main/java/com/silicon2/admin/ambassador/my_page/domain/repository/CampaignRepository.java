package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.Campaign;

import java.util.Optional;

public interface CampaignRepository {
    Optional<Campaign> findById(Long id);
}
