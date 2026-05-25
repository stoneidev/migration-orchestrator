package com.silicon2.admin.shop.mp_settings.adapter.in.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.silicon2.admin.shop.mp_settings.application.DeleteAccountUseCase;
import com.silicon2.admin.shop.mp_settings.application.GetAccountSettingsUseCase;
import com.silicon2.admin.shop.mp_settings.application.UpdateAccountSettingsUseCase;
import com.silicon2.admin.shop.mp_settings.application.dto.AccountSettingsResponse;
import com.silicon2.admin.shop.mp_settings.application.dto.DeleteAccountRequest;
import com.silicon2.admin.shop.mp_settings.application.dto.UpdateAccountSettingsRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.doNothing;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(AccountSettingsController.class)
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

    @Test
    @DisplayName("계정 설정 조회 API 성공")
    void getAccountSettings_success() throws Exception {
        // given
        Long memberId = 1L;
        AccountSettingsResponse response = AccountSettingsResponse.builder()
                .memberId(memberId)
                .email("test@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .build();

        given(getAccountSettingsUseCase.execute(memberId))
                .willReturn(response);

        // when & then
        mockMvc.perform(get("/api/shop/mp-settings")
                        .param("memberId", String.valueOf(memberId)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.memberId").value(memberId))
                .andExpect(jsonPath("$.email").value("test@example.com"))
                .andExpect(jsonPath("$.name").value("홍길동"))
                .andExpect(jsonPath("$.phone").value("010-1234-5678"))
                .andExpect(jsonPath("$.emailNotificationEnabled").value(true))
                .andExpect(jsonPath("$.smsNotificationEnabled").value(false));
    }

    @Test
    @DisplayName("계정 설정 업데이트 API 성공")
    void updateAccountSettings_success() throws Exception {
        // given
        UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                .memberId(1L)
                .email("new@example.com")
                .name("홍길동")
                .phone("010-9999-9999")
                .emailNotificationEnabled(false)
                .smsNotificationEnabled(true)
                .build();

        doNothing().when(updateAccountSettingsUseCase).execute(any(UpdateAccountSettingsRequest.class));

        // when & then
        mockMvc.perform(post("/api/shop/mp-settings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("계정 삭제 API 성공")
    void deleteAccount_success() throws Exception {
        // given
        DeleteAccountRequest request = DeleteAccountRequest.builder()
                .memberId(1L)
                .password("password123")
                .build();

        doNothing().when(deleteAccountUseCase).execute(any(DeleteAccountRequest.class));

        // when & then
        mockMvc.perform(post("/api/shop/mp-settings/delete")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk());
    }
}
