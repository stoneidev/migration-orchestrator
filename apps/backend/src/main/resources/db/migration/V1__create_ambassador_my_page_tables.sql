CREATE TABLE IF NOT EXISTS ambassador_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    tier_code VARCHAR(20),
    total_commission INT DEFAULT 0,
    current_month_commission INT DEFAULT 0,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    profile_image_url VARCHAR(500),
    nickname VARCHAR(50),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    banned_at TIMESTAMP NULL,
    ban_reason VARCHAR(500),
    affiliate_member_id BIGINT,
    INDEX idx_member_id (member_id),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS ambassador_member_sns (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ambassador_member_id BIGINT NOT NULL,
    sns_type VARCHAR(20) NOT NULL,
    sns_id VARCHAR(100),
    sns_url VARCHAR(500),
    follower_count INT DEFAULT 0,
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ambassador_member_id (ambassador_member_id),
    INDEX idx_sns_type (sns_type)
);

CREATE TABLE IF NOT EXISTS ambassador_campaign_image (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    ambassador_member_id BIGINT NOT NULL,
    image_type VARCHAR(20) DEFAULT 'REVIEW',
    image_url VARCHAR(500) NOT NULL,
    display_order INT DEFAULT 1,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_campaign_ambassador (campaign_id, ambassador_member_id),
    INDEX idx_image_type (image_type)
);

CREATE TABLE IF NOT EXISTS affiliate_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    affiliate_code VARCHAR(50) NOT NULL UNIQUE,
    tracking_url VARCHAR(500),
    total_earnings INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_id (member_id),
    INDEX idx_affiliate_code (affiliate_code)
);
