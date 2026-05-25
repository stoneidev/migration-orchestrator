package com.silicon2.admin.shop.mp_profile.adapter.in.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.silicon2.admin.shop.mp_profile.application.GetBeautyProfileUseCase;
import com.silicon2.admin.shop.mp_profile.application.SaveBeautyProfileUseCase;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;
import java.util.Collections;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(BeautyProfileController.class)
@DisplayName("BeautyProfileController 테스트")
class BeautyProfileControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private GetBeautyProfileUseCase getBeautyProfileUseCase;

    @MockBean
    private SaveBeautyProfileUseCase saveBeautyProfileUseCase;

    @Test
    @DisplayName("GET /v1/shop/profile - 존재하는 프로필 조회")
    void testGetBeautyProfile_Existing() throws Exception {
        // given
        String userId = "user123";
        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender("FEMALE");
        response.setAgeGroup("20-29");
        response.setSkinType("OILY");
        response.setSkinConcern(Arrays.asList("ACNE", "WRINKLES"));
        response.setHealthConcern(Arrays.asList("HYDRATION"));
        response.setCleanBeautyPreferences(Arrays.asList("VEGAN"));
        response.setHairConcern(Collections.emptyList());

        given(getBeautyProfileUseCase.execute(userId)).willReturn(response);

        // when & then
        mockMvc.perform(get("/v1/shop/profile")
                        .param("userId", userId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.gender").value("FEMALE"))
                .andExpect(jsonPath("$.data.ageGroup").value("20-29"))
                .andExpect(jsonPath("$.data.skinType").value("OILY"))
                .andExpect(jsonPath("$.data.skinConcern[0]").value("ACNE"))
                .andExpect(jsonPath("$.data.skinConcern[1]").value("WRINKLES"));

        verify(getBeautyProfileUseCase).execute(userId);
    }

    @Test
    @DisplayName("GET /v1/shop/profile - 존재하지 않는 프로필 조회")
    void testGetBeautyProfile_NotFound() throws Exception {
        // given
        String userId = "nonexistent";
        given(getBeautyProfileUseCase.execute(userId)).willReturn(null);

        // when & then
        mockMvc.perform(get("/v1/shop/profile")
                        .param("userId", userId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isEmpty());

        verify(getBeautyProfileUseCase).execute(userId);
    }

    @Test
    @DisplayName("GET /v1/shop/profile - userId 파라미터 없이 호출 시 기본값 사용")
    void testGetBeautyProfile_DefaultUserId() throws Exception {
        // given
        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender("MALE");
        given(getBeautyProfileUseCase.execute("user123")).willReturn(response);

        // when & then
        mockMvc.perform(get("/v1/shop/profile"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.gender").value("MALE"));

        verify(getBeautyProfileUseCase).execute("user123");
    }

    @Test
    @DisplayName("POST /v1/shop/profile - 프로필 생성")
    void testCreateBeautyProfile() throws Exception {
        // given
        String userId = "newuser";
        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("FEMALE");
        request.setAgeGroup("30-39");
        request.setSkinType("DRY");
        request.setSkinConcern(Arrays.asList("WRINKLES", "DULLNESS"));
        request.setHealthConcern(Arrays.asList("HYDRATION"));
        request.setCleanBeautyPreferences(Arrays.asList("VEGAN", "CRUELTY_FREE"));
        request.setHairConcern(Arrays.asList("SPLIT_ENDS"));

        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender(request.getGender());
        response.setAgeGroup(request.getAgeGroup());
        response.setSkinType(request.getSkinType());
        response.setSkinConcern(request.getSkinConcern());
        response.setHealthConcern(request.getHealthConcern());
        response.setCleanBeautyPreferences(request.getCleanBeautyPreferences());
        response.setHairConcern(request.getHairConcern());

        given(saveBeautyProfileUseCase.execute(eq(userId), any(BeautyProfileRequest.class)))
                .willReturn(response);

        // when & then
        mockMvc.perform(post("/v1/shop/profile")
                        .param("userId", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.gender").value("FEMALE"))
                .andExpect(jsonPath("$.data.ageGroup").value("30-39"))
                .andExpect(jsonPath("$.data.skinType").value("DRY"))
                .andExpect(jsonPath("$.data.skinConcern[0]").value("WRINKLES"))
                .andExpect(jsonPath("$.data.skinConcern[1]").value("DULLNESS"))
                .andExpect(jsonPath("$.data.healthConcern[0]").value("HYDRATION"))
                .andExpect(jsonPath("$.data.cleanBeautyPreferences[0]").value("VEGAN"))
                .andExpect(jsonPath("$.data.cleanBeautyPreferences[1]").value("CRUELTY_FREE"))
                .andExpect(jsonPath("$.data.hairConcern[0]").value("SPLIT_ENDS"));

        verify(saveBeautyProfileUseCase).execute(eq(userId), any(BeautyProfileRequest.class));
    }

    @Test
    @DisplayName("POST /v1/shop/profile - 빈 리스트로 프로필 생성")
    void testCreateBeautyProfile_EmptyLists() throws Exception {
        // given
        String userId = "user456";
        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("MALE");
        request.setSkinConcern(Collections.emptyList());
        request.setHealthConcern(Collections.emptyList());
        request.setCleanBeautyPreferences(Collections.emptyList());
        request.setHairConcern(Collections.emptyList());

        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender("MALE");
        response.setSkinConcern(Collections.emptyList());
        response.setHealthConcern(Collections.emptyList());
        response.setCleanBeautyPreferences(Collections.emptyList());
        response.setHairConcern(Collections.emptyList());

        given(saveBeautyProfileUseCase.execute(eq(userId), any(BeautyProfileRequest.class)))
                .willReturn(response);

        // when & then
        mockMvc.perform(post("/v1/shop/profile")
                        .param("userId", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.gender").value("MALE"))
                .andExpect(jsonPath("$.data.skinConcern").isEmpty())
                .andExpect(jsonPath("$.data.healthConcern").isEmpty())
                .andExpect(jsonPath("$.data.cleanBeautyPreferences").isEmpty())
                .andExpect(jsonPath("$.data.hairConcern").isEmpty());
    }

    @Test
    @DisplayName("POST /v1/shop/profile - userId 파라미터 없이 호출 시 기본값 사용")
    void testCreateBeautyProfile_DefaultUserId() throws Exception {
        // given
        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("FEMALE");

        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender("FEMALE");

        given(saveBeautyProfileUseCase.execute(eq("user123"), any(BeautyProfileRequest.class)))
                .willReturn(response);

        // when & then
        mockMvc.perform(post("/v1/shop/profile")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));

        verify(saveBeautyProfileUseCase).execute(eq("user123"), any(BeautyProfileRequest.class));
    }
}
