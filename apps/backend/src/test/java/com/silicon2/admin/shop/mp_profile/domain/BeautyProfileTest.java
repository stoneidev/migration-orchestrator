package com.silicon2.admin.shop.mp_profile.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("BeautyProfile 도메인 모델 테스트")
class BeautyProfileTest {

    @Test
    @DisplayName("BeautyProfile 생성 시 생성일시와 수정일시가 자동 설정된다")
    void testPrePersist() {
        // given
        BeautyProfile profile = new BeautyProfile();
        profile.setUserId("user123");
        profile.setGender("FEMALE");
        profile.setSkinType("OILY");

        // when
        profile.onCreate();

        // then
        assertThat(profile.getCreatedAt()).isNotNull();
        assertThat(profile.getUpdatedAt()).isNotNull();
    }

    @Test
    @DisplayName("BeautyProfile 수정 시 수정일시가 갱신된다")
    void testPreUpdate() {
        // given
        BeautyProfile profile = new BeautyProfile();
        profile.setUserId("user123");
        profile.onCreate();
        LocalDateTime originalUpdatedAt = profile.getUpdatedAt();

        // when
        try {
            Thread.sleep(10); // 시간 차이를 만들기 위해
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        profile.onUpdate();

        // then
        assertThat(profile.getUpdatedAt()).isAfter(originalUpdatedAt);
    }

    @Test
    @DisplayName("BeautyProfile의 모든 필드가 정상적으로 설정된다")
    void testAllFieldsSetting() {
        // given
        BeautyProfile profile = new BeautyProfile();

        // when
        profile.setId(1L);
        profile.setUserId("user456");
        profile.setGender("MALE");
        profile.setAgeGroup("20-29");
        profile.setSkinTone("LIGHT");
        profile.setSkinConcern("ACNE,WRINKLES");
        profile.setHealthConcern("HYDRATION");
        profile.setCleanBeautyPreferences("VEGAN,CRUELTY_FREE");
        profile.setSkinType("COMBINATION");
        profile.setHairConcern("DANDRUFF");
        LocalDateTime now = LocalDateTime.now();
        profile.setCreatedAt(now);
        profile.setUpdatedAt(now);

        // then
        assertThat(profile.getId()).isEqualTo(1L);
        assertThat(profile.getUserId()).isEqualTo("user456");
        assertThat(profile.getGender()).isEqualTo("MALE");
        assertThat(profile.getAgeGroup()).isEqualTo("20-29");
        assertThat(profile.getSkinTone()).isEqualTo("LIGHT");
        assertThat(profile.getSkinConcern()).isEqualTo("ACNE,WRINKLES");
        assertThat(profile.getHealthConcern()).isEqualTo("HYDRATION");
        assertThat(profile.getCleanBeautyPreferences()).isEqualTo("VEGAN,CRUELTY_FREE");
        assertThat(profile.getSkinType()).isEqualTo("COMBINATION");
        assertThat(profile.getHairConcern()).isEqualTo("DANDRUFF");
        assertThat(profile.getCreatedAt()).isEqualTo(now);
        assertThat(profile.getUpdatedAt()).isEqualTo(now);
    }
}
