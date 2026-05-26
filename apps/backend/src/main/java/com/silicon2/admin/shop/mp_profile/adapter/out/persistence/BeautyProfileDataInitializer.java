package com.silicon2.admin.shop.mp_profile.adapter.out.persistence;

import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component("beautyProfileDataInitializer")
@Profile("nomysql")
@RequiredArgsConstructor
public class BeautyProfileDataInitializer implements CommandLineRunner {

    private final BeautyProfileRepository repository;

    @Override
    public void run(String... args) {
        if (repository.count() > 0) {
            return;
        }

        // User 1: Complete profile
        BeautyProfile profile1 = new BeautyProfile();
        profile1.setUserId("user123");
        profile1.setGender("Female");
        profile1.setAgeGroup("20s");
        profile1.setSkinTone("Porcelain");
        profile1.setSkinConcern("Acne,Sensitivity");
        profile1.setHealthConcern("Allergies");
        profile1.setCleanBeautyPreferences("Vegan,Cruelty-free");
        profile1.setSkinType("Combination");
        profile1.setHairConcern("Frizz,Dryness");
        profile1.setCreatedAt(LocalDateTime.now().minusDays(30));
        profile1.setUpdatedAt(LocalDateTime.now().minusDays(5));

        // User 2: Minimal profile
        BeautyProfile profile2 = new BeautyProfile();
        profile2.setUserId("user456");
        profile2.setGender("Male");
        profile2.setAgeGroup("30s");
        profile2.setSkinTone("Fair");
        profile2.setSkinConcern("Wrinkles");
        profile2.setHealthConcern("");
        profile2.setCleanBeautyPreferences("Organic");
        profile2.setSkinType("Dry");
        profile2.setHairConcern("");
        profile2.setCreatedAt(LocalDateTime.now().minusDays(20));
        profile2.setUpdatedAt(LocalDateTime.now().minusDays(10));

        // User 3: Multiple concerns
        BeautyProfile profile3 = new BeautyProfile();
        profile3.setUserId("user789");
        profile3.setGender("Female");
        profile3.setAgeGroup("40s");
        profile3.setSkinTone("Medium");
        profile3.setSkinConcern("Wrinkles,Dark Spots,Dryness");
        profile3.setHealthConcern("Diabetes,Allergies");
        profile3.setCleanBeautyPreferences("Vegan,Organic,Cruelty-free");
        profile3.setSkinType("Dry");
        profile3.setHairConcern("Hair Loss,Dryness");
        profile3.setCreatedAt(LocalDateTime.now().minusDays(15));
        profile3.setUpdatedAt(LocalDateTime.now().minusDays(2));

        // User 4: Young user
        BeautyProfile profile4 = new BeautyProfile();
        profile4.setUserId("user101");
        profile4.setGender("Female");
        profile4.setAgeGroup("Teens");
        profile4.setSkinTone("Porcelain");
        profile4.setSkinConcern("Acne,Oiliness");
        profile4.setHealthConcern("");
        profile4.setCleanBeautyPreferences("Cruelty-free");
        profile4.setSkinType("Oily");
        profile4.setHairConcern("Oiliness");
        profile4.setCreatedAt(LocalDateTime.now().minusDays(7));
        profile4.setUpdatedAt(LocalDateTime.now().minusDays(1));

        // User 5: Mature user
        BeautyProfile profile5 = new BeautyProfile();
        profile5.setUserId("user202");
        profile5.setGender("Female");
        profile5.setAgeGroup("50s");
        profile5.setSkinTone("Olive");
        profile5.setSkinConcern("Wrinkles,Sagging,Dark Spots");
        profile5.setHealthConcern("High Blood Pressure");
        profile5.setCleanBeautyPreferences("Organic,Vegan");
        profile5.setSkinType("Dry");
        profile5.setHairConcern("Hair Loss,Gray Hair");
        profile5.setCreatedAt(LocalDateTime.now().minusDays(45));
        profile5.setUpdatedAt(LocalDateTime.now().minusDays(3));

        // User 6: Male user with concerns
        BeautyProfile profile6 = new BeautyProfile();
        profile6.setUserId("user303");
        profile6.setGender("Male");
        profile6.setAgeGroup("20s");
        profile6.setSkinTone("Fair");
        profile6.setSkinConcern("Acne,Oiliness");
        profile6.setHealthConcern("");
        profile6.setCleanBeautyPreferences("");
        profile6.setSkinType("Oily");
        profile6.setHairConcern("Dandruff");
        profile6.setCreatedAt(LocalDateTime.now().minusDays(12));
        profile6.setUpdatedAt(LocalDateTime.now().minusDays(8));

        // User 7: Sensitive skin focus
        BeautyProfile profile7 = new BeautyProfile();
        profile7.setUserId("user404");
        profile7.setGender("Female");
        profile7.setAgeGroup("30s");
        profile7.setSkinTone("Porcelain");
        profile7.setSkinConcern("Sensitivity,Redness");
        profile7.setHealthConcern("Allergies,Eczema");
        profile7.setCleanBeautyPreferences("Vegan,Cruelty-free,Organic,Fragrance-free");
        profile7.setSkinType("Sensitive");
        profile7.setHairConcern("Sensitivity");
        profile7.setCreatedAt(LocalDateTime.now().minusDays(25));
        profile7.setUpdatedAt(LocalDateTime.now().minusDays(4));

        // User 8: Combination skin
        BeautyProfile profile8 = new BeautyProfile();
        profile8.setUserId("user505");
        profile8.setGender("Female");
        profile8.setAgeGroup("20s");
        profile8.setSkinTone("Medium");
        profile8.setSkinConcern("Oiliness,Dryness");
        profile8.setHealthConcern("");
        profile8.setCleanBeautyPreferences("Cruelty-free");
        profile8.setSkinType("Combination");
        profile8.setHairConcern("Frizz");
        profile8.setCreatedAt(LocalDateTime.now().minusDays(18));
        profile8.setUpdatedAt(LocalDateTime.now().minusDays(6));

        // User 9: Dark complexion
        BeautyProfile profile9 = new BeautyProfile();
        profile9.setUserId("user606");
        profile9.setGender("Male");
        profile9.setAgeGroup("30s");
        profile9.setSkinTone("Deep");
        profile9.setSkinConcern("Dark Spots,Oiliness");
        profile9.setHealthConcern("");
        profile9.setCleanBeautyPreferences("Vegan");
        profile9.setSkinType("Oily");
        profile9.setHairConcern("Dryness");
        profile9.setCreatedAt(LocalDateTime.now().minusDays(22));
        profile9.setUpdatedAt(LocalDateTime.now().minusDays(11));

        // User 10: Comprehensive profile
        BeautyProfile profile10 = new BeautyProfile();
        profile10.setUserId("user707");
        profile10.setGender("Female");
        profile10.setAgeGroup("40s");
        profile10.setSkinTone("Olive");
        profile10.setSkinConcern("Wrinkles,Dark Spots,Dryness,Sensitivity");
        profile10.setHealthConcern("Allergies,High Blood Pressure");
        profile10.setCleanBeautyPreferences("Vegan,Organic,Cruelty-free,Fragrance-free");
        profile10.setSkinType("Sensitive");
        profile10.setHairConcern("Hair Loss,Dryness,Gray Hair");
        profile10.setCreatedAt(LocalDateTime.now().minusDays(60));
        profile10.setUpdatedAt(LocalDateTime.now());

        repository.save(profile1);
        repository.save(profile2);
        repository.save(profile3);
        repository.save(profile4);
        repository.save(profile5);
        repository.save(profile6);
        repository.save(profile7);
        repository.save(profile8);
        repository.save(profile9);
        repository.save(profile10);

        System.out.println("Initialized 10 beauty profiles");
    }
}
