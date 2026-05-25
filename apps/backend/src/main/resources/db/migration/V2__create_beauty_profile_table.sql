CREATE TABLE IF NOT EXISTS mp_beauty_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    gender VARCHAR(50),
    age_group VARCHAR(50),
    skin_tone VARCHAR(50),
    skin_concern TEXT,
    health_concern TEXT,
    clean_beauty_preferences TEXT,
    skin_type VARCHAR(50),
    hair_concern TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id)
);
