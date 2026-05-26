package com.silicon2.admin.shop.mp_profile.domain.model;

import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;

import static org.assertj.core.api.BDDAssertions.then;

@DisplayName("BeautyProfile")
class BeautyProfileTest {

    @Nested
    @DisplayName("프로필 생성 시")
    class WhenCreating {

        @Test
        @DisplayName("userId가 설정된 빈 프로필을 생성한다")
        void shouldCreateProfileForUser() {
            BeautyProfile profile = Bdd.when(() -> BeautyProfile.createForUser("user123"));

            Bdd.then(() -> {
                then(profile.getUserId()).isEqualTo("user123");
                then(profile.getGender()).isNull();
            });
        }
    }

    @Nested
    @DisplayName("속성 업데이트 시")
    class WhenUpdatingAttributes {

        @Test
        @DisplayName("리스트 필드를 콤마 구분 문자열로 저장한다")
        void shouldJoinListFields() {
            BeautyProfile profile = BeautyProfile.createForUser("user123");

            Bdd.when(() -> profile.updateAttributes(
                    "FEMALE", "20s", "Porcelain",
                    Arrays.asList("ACNE", "WRINKLES"),
                    Collections.emptyList(),
                    Arrays.asList("VEGAN"),
                    "OILY", null
            ));

            Bdd.then(() -> {
                then(profile.getSkinConcern()).isEqualTo("ACNE,WRINKLES");
                then(profile.getHealthConcern()).isEmpty();
                then(profile.getCleanBeautyPreferences()).isEqualTo("VEGAN");
            });
        }
    }

    @Nested
    @DisplayName("리스트 필드 조회 시")
    class WhenReadingListFields {

        @Test
        @DisplayName("콤마 구분 문자열을 리스트로 파싱한다")
        void shouldParseCommaSeparatedValues() {
            BeautyProfile profile = new BeautyProfile();
            profile.setSkinConcern("ACNE,WRINKLES");
            profile.setHealthConcern("");
            profile.setHairConcern("DANDRUFF");

            Bdd.then(() -> {
                then(profile.getSkinConcernAsList()).containsExactly("ACNE", "WRINKLES");
                then(profile.getHealthConcernAsList()).isEmpty();
                then(profile.getHairConcernAsList()).containsExactly("DANDRUFF");
            });
        }
    }

    @Nested
    @DisplayName("필드 설정 시")
    class WhenSettingFields {

        @Test
        @DisplayName("모든 필드가 정상적으로 설정된다")
        void shouldSetAllFields() {
            LocalDateTime now = LocalDateTime.now();
            BeautyProfile profile = new BeautyProfile();

            Bdd.when(() -> {
                profile.setId(1L);
                profile.setUserId("user456");
                profile.setGender("MALE");
                profile.setAgeGroup("20-29");
                profile.setSkinTone("LIGHT");
                profile.setSkinConcern("ACNE,WRINKLES");
                profile.setCreatedAt(now);
                profile.setUpdatedAt(now);
            });

            Bdd.then(() -> {
                then(profile.getId()).isEqualTo(1L);
                then(profile.getUserId()).isEqualTo("user456");
                then(profile.getGender()).isEqualTo("MALE");
                then(profile.getCreatedAt()).isEqualTo(now);
            });
        }
    }
}
