package com.silicon2.admin.shop.mp_profile.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "mp_beauty_profiles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class BeautyProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String userId;

    private String gender;

    @Column(name = "age_group")
    private String ageGroup;

    @Column(name = "skin_tone")
    private String skinTone;

    @Column(name = "skin_concern", columnDefinition = "TEXT")
    private String skinConcern; // Stored as comma-separated values

    @Column(name = "health_concern", columnDefinition = "TEXT")
    private String healthConcern; // Stored as comma-separated values

    @Column(name = "clean_beauty_preferences", columnDefinition = "TEXT")
    private String cleanBeautyPreferences; // Stored as comma-separated values

    @Column(name = "skin_type")
    private String skinType;

    @Column(name = "hair_concern", columnDefinition = "TEXT")
    private String hairConcern; // Stored as comma-separated values

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        if (updatedAt == null) {
            updatedAt = LocalDateTime.now();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
