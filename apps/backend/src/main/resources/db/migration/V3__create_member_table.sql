CREATE TABLE IF NOT EXISTS member_table (
    member_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    email_notification_enabled BOOLEAN DEFAULT TRUE,
    sms_notification_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_member_email ON member_table(email);
CREATE INDEX idx_member_created_at ON member_table(created_at);

-- affiliate_member_table for business rules BR007
CREATE TABLE IF NOT EXISTS affiliate_member_table (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    points INT DEFAULT 0,
    expired_points INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES member_table(member_id) ON DELETE CASCADE
);

CREATE INDEX idx_affiliate_member_id ON affiliate_member_table(member_id);
