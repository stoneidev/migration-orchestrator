package com.silicon2.admin.ambassador.my_page.domain.service;

import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SnsLinkGenerationService {

    public String generateTrackingLink(AffiliateMember affiliateMember, String baseUrl, Long campaignId) {
        if (affiliateMember == null) {
            throw new IllegalStateException("Ambassador must have a linked affiliate member to generate SNS links");
        }

        String trackingCode = affiliateMember.getTrackingCode();
        if (trackingCode == null || trackingCode.isEmpty()) {
            trackingCode = generateTrackingCode();
        }

        return String.format("%s?ref=%s&campaign=%d&ts=%d",
            baseUrl,
            trackingCode,
            campaignId,
            System.currentTimeMillis());
    }

    private String generateTrackingCode() {
        return "AMB-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    public void validateSnsAccountExists(int snsAccountCount) {
        if (snsAccountCount < 1) {
            throw new IllegalStateException("At least one SNS account must be registered before generating a share link");
        }
    }
}
