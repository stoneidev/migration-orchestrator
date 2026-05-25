package com.silicon2.admin.shop.mp_settings.adapter.out.persistence;

import com.silicon2.admin.shop.mp_settings.adapter.out.persistence.entity.MemberEntity;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Slf4j
@Component("mpSettingsDataInitializer")
@Profile("nomysql")
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final MpSettingsMemberJpaRepository memberJpaRepository;

    @Override
    public void run(String... args) {
        if (memberJpaRepository.count() == 0) {
            log.info("Initializing member test data...");

            MemberEntity member1 = MemberEntity.builder()
                    .email("test1@example.com")
                    .name("홍길동")
                    .phone("010-1234-5678")
                    .passwordHash("$2a$10$hashedPassword1")
                    .emailNotificationEnabled(true)
                    .smsNotificationEnabled(false)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            MemberEntity member2 = MemberEntity.builder()
                    .email("test2@example.com")
                    .name("김철수")
                    .phone("010-9876-5432")
                    .passwordHash("$2a$10$hashedPassword2")
                    .emailNotificationEnabled(false)
                    .smsNotificationEnabled(true)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            memberJpaRepository.save(member1);
            memberJpaRepository.save(member2);

            log.info("Member test data initialized successfully");
        }
    }
}
