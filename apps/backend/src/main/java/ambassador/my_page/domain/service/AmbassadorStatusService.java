package com.silicon2.admin.ambassador.my_page.domain.service;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AmbassadorStatusService {

    public void validateAccess(AmbassadorMember member) {
        if (!member.canAccessPage()) {
            if (member.getBannedAt() != null) {
                throw new IllegalStateException("Ambassador is banned: " + member.getBanReason());
            }
            throw new IllegalStateException("Ambassador is not active");
        }
    }

    public boolean hasAffiliateLink(AmbassadorMember member) {
        return member.isActive();
    }
}
