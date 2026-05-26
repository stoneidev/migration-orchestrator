package com.silicon2.admin.shop.mp_profile.adapter.in.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.silicon2.admin.shop.mp_profile.application.GetBeautyProfileUseCase;
import com.silicon2.admin.shop.mp_profile.application.SaveBeautyProfileUseCase;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import java.util.Arrays;
import java.util.Collections;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(BeautyProfileController.class)
@DisplayName("BeautyProfileController")
class BeautyProfileControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private GetBeautyProfileUseCase getBeautyProfileUseCase;

    @MockBean
    private SaveBeautyProfileUseCase saveBeautyProfileUseCase;

    @Nested
    @DisplayName("GET /v1/shop/profile")
    class WhenGettingProfile {

        @Test
        @DisplayName("존재하는 프로필을 조회하면 200과 데이터를 반환한다")
        void shouldReturnExistingProfile() throws Exception {
            Bdd.given(() -> {
                BeautyProfileResponse response = new BeautyProfileResponse();
                response.setGender("FEMALE");
                response.setAgeGroup("20-29");
                response.setSkinType("OILY");
                response.setSkinConcern(Arrays.asList("ACNE", "WRINKLES"));
                given(getBeautyProfileUseCase.execute("user123")).willReturn(response);
            });

            ResultActions result = Bdd.when(() -> mockMvc.perform(get("/v1/shop/profile")
                    .param("userId", "user123")));

            Bdd.then(() -> {
                result.andExpect(status().isOk())
                        .andExpect(jsonPath("$.success").value(true))
                        .andExpect(jsonPath("$.data.gender").value("FEMALE"));
                verify(getBeautyProfileUseCase).execute("user123");
            });
        }

        @Test
        @DisplayName("존재하지 않는 프로필이면 data 필드 없이 반환한다")
        void shouldReturnEmptyWhenNotFound() throws Exception {
            Bdd.given(() -> given(getBeautyProfileUseCase.execute("nonexistent")).willReturn(null));

            Bdd.when(() -> mockMvc.perform(get("/v1/shop/profile").param("userId", "nonexistent")))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data").doesNotExist());
        }
    }

    @Nested
    @DisplayName("POST /v1/shop/profile")
    class WhenSavingProfile {

        @Test
        @DisplayName("프로필을 생성하면 200과 저장된 데이터를 반환한다")
        void shouldCreateProfile() throws Exception {
            BeautyProfileRequest request = new BeautyProfileRequest();
            request.setGender("FEMALE");
            request.setSkinConcern(Arrays.asList("WRINKLES", "DULLNESS"));

            BeautyProfileResponse response = new BeautyProfileResponse();
            response.setGender("FEMALE");
            response.setSkinConcern(Arrays.asList("WRINKLES", "DULLNESS"));

            Bdd.given(() -> given(saveBeautyProfileUseCase.execute(eq("newuser"), any(BeautyProfileRequest.class)))
                    .willReturn(response));

            Bdd.when(() -> mockMvc.perform(post("/v1/shop/profile")
                            .param("userId", "newuser")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request))))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.gender").value("FEMALE"))
                    .andExpect(jsonPath("$.data.skinConcern[0]").value("WRINKLES"));
        }

        @Test
        @DisplayName("빈 리스트로 프로필을 생성할 수 있다")
        void shouldAcceptEmptyLists() throws Exception {
            BeautyProfileRequest request = new BeautyProfileRequest();
            request.setGender("MALE");
            request.setSkinConcern(Collections.emptyList());

            BeautyProfileResponse response = new BeautyProfileResponse();
            response.setGender("MALE");
            response.setSkinConcern(Collections.emptyList());

            Bdd.given(() -> given(saveBeautyProfileUseCase.execute(eq("user456"), any(BeautyProfileRequest.class)))
                    .willReturn(response));

            Bdd.when(() -> mockMvc.perform(post("/v1/shop/profile")
                            .param("userId", "user456")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request))))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.skinConcern").isEmpty());
        }
    }
}
