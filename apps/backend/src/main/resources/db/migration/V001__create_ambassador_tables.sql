-- Ambassador Member Table
CREATE TABLE ambassador_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    joined_at TIMESTAMP NULL,
    banned_at TIMESTAMP NULL,
    ban_reason VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_member_id (member_id),
    INDEX idx_status (status),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ambassador Member SNS Table
CREATE TABLE ambassador_member_sns (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ambassador_member_id BIGINT NOT NULL,
    sns_type VARCHAR(20) NOT NULL,
    sns_account_id VARCHAR(100) NOT NULL,
    sns_account_url VARCHAR(500),
    follower_count INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ambassador_member_id (ambassador_member_id),
    INDEX idx_sns_type (sns_type),
    UNIQUE KEY uk_ambassador_sns (ambassador_member_id, sns_type, sns_account_id),
    FOREIGN KEY (ambassador_member_id) REFERENCES ambassador_member(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ambassador Campaign Table
CREATE TABLE ambassador_campaign (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ambassador Campaign Image Table
CREATE TABLE ambassador_campaign_image (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    ambassador_member_id BIGINT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_type VARCHAR(20) DEFAULT 'REVIEW',
    display_order INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_campaign_id (campaign_id),
    INDEX idx_ambassador_member_id (ambassador_member_id),
    FOREIGN KEY (campaign_id) REFERENCES ambassador_campaign(id) ON DELETE CASCADE,
    FOREIGN KEY (ambassador_member_id) REFERENCES ambassador_member(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ambassador Review Table
CREATE TABLE ambassador_review (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    ambassador_member_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    image_urls TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_campaign_id (campaign_id),
    INDEX idx_ambassador_member_id (ambassador_member_id),
    INDEX idx_status (status),
    UNIQUE KEY uk_campaign_ambassador (campaign_id, ambassador_member_id),
    FOREIGN KEY (campaign_id) REFERENCES ambassador_campaign(id) ON DELETE CASCADE,
    FOREIGN KEY (ambassador_member_id) REFERENCES ambassador_member(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Affiliate Member Table
CREATE TABLE affiliate_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ambassador_member_id BIGINT NOT NULL,
    affiliate_code VARCHAR(50) NOT NULL UNIQUE,
    tracking_code VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ambassador_member_id (ambassador_member_id),
    INDEX idx_affiliate_code (affiliate_code),
    INDEX idx_tracking_code (tracking_code),
    UNIQUE KEY uk_ambassador_affiliate (ambassador_member_id),
    FOREIGN KEY (ambassador_member_id) REFERENCES ambassador_member(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
