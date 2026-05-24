-- Ambassador Member Table
CREATE TABLE ambassador_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    approved_at TIMESTAMP NULL,
    banned_at TIMESTAMP NULL,
    ban_reason VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_member_id (member_id),
    INDEX idx_status (status),
    INDEX idx_member_id (member_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ambassador Member SNS Table
CREATE TABLE ambassador_member_sns (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ambassador_member_id BIGINT NOT NULL,
    sns_type VARCHAR(50) NOT NULL,
    sns_handle VARCHAR(100) NULL,
    sns_url VARCHAR(500) NULL,
    follower_count INT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ambassador_member_id (ambassador_member_id),
    INDEX idx_sns_type (sns_type),
    CONSTRAINT fk_ambassador_member_sns_member
        FOREIGN KEY (ambassador_member_id)
        REFERENCES ambassador_member(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ambassador Campaign Image Table
CREATE TABLE ambassador_campaign_image (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ambassador_member_id BIGINT NOT NULL,
    campaign_id BIGINT NOT NULL,
    image_url VARCHAR(1000) NOT NULL,
    display_order INT NULL,
    image_type VARCHAR(50) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ambassador_campaign (ambassador_member_id, campaign_id),
    INDEX idx_campaign_id (campaign_id),
    CONSTRAINT fk_ambassador_campaign_image_member
        FOREIGN KEY (ambassador_member_id)
        REFERENCES ambassador_member(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Affiliate Member Table
CREATE TABLE affiliate_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    tracking_code VARCHAR(50) UNIQUE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_member_id (member_id),
    UNIQUE KEY uk_tracking_code (tracking_code),
    INDEX idx_tracking_code (tracking_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
