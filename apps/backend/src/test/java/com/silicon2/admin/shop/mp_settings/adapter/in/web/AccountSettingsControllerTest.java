package com.silicon2.admin.shop.mp_settings.adapter.in.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.silicon2.admin.shop.mp_settings.application.DeleteAccountUseCase;
import com.silicon2.admin.shop.mp_settings.application.GetAccountSettingsUseCase;
import com.silicon2.admin.shop.mp_settings.application.UpdateAccountSettingsUseCase;
import com.silicon2.admin.shop.mp_settings.application.dto.AccountSettingsResponse;
import com.silicon2.admin.shop.mp_settings.application.dto.DeleteAccountRequest;
import com.silicon2.admin.shop.mp_settings.application.dto.UpdateAccountSettingsRequest;
import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.willDoNothing;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(AccountSettingsController.class)
@DisplayName("AccountSettingsController")
class AccountSettingsControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private GetAccountSettingsUseCase getAccountSettingsUseCase;

    @MockBean
    private UpdateAccountSettingsUseCase updateAccountSettingsUseCase;

    @MockBean
    private DeleteAccountUseCase deleteAccountUseCase;

    @Nested
    @DisplayName("GET /shop/mp-settings")
    class WhenGettingSettings {

        @Test
        @DisplayName("계정 설정을 조회하면 200과 설정 데이터를 반환한다")
        void shouldReturnAccountSettings() throws Exception {
            Bdd.given(() -> given(getAccountSettingsUseCase.execute(1L))
                    .willReturn(AccountSettingsResponse.builder()
                            .memberId(1L)
                            .email("test@example.com")
                            .name("홍길동")
                            .phone("010-1234-5678")
                            .emailNotificationEnabled(true)
                            .smsNotificationEnabled(false)
                            .build()));

            Bdd.when(() -> mockMvc.perform(get("/shop/mp-settings").param("memberId", "1")))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.email").value("test@example.com"))
                    .andExpect(jsonPath("$.name").value("홍길동"));
        }
    }

    @Nested
    @DisplayName("POST /shop/mp-settings")
    class WhenUpdatingSettings {

        @Test
        @DisplayName("계정 설정을 업데이트하면 200을 반환한다")
        void shouldUpdateSettings() throws Exception {
            UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                    .memberId(1L)
                    .email("new@example.com")
                    .build();

            Bdd.given(() -> willDoNothing().given(updateAccountSettingsUseCase)
                    .execute(any(UpdateAccountSettingsRequest.class)));

            Bdd.when(() -> mockMvc.perform(post("/shop/mp-settings")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request))))
                    .andExpect(status().isOk());
        }
    }

    @Nested
    @DisplayName("POST /shop/mp-settings/delete")
    class WhenDeletingAccount {

        @Test
        @DisplayName("계정을 삭제하면 200을 반환한다")
        void shouldDeleteAccount() throws Exception {
            DeleteAccountRequest request = DeleteAccountRequest.builder()
                    .memberId(1L)
                    .password("password123")
                    .build();

            Bdd.given(() -> willDoNothing().given(deleteAccountUseCase)
                    .execute(any(DeleteAccountRequest.class)));

            Bdd.when(() -> mockMvc.perform(post("/shop/mp-settings/delete")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request))))
                    .andExpect(status().isOk());
        }
    }
}
