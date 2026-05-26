package com.silicon2.admin.ambassador.my_page.adapter.in.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.silicon2.admin.ambassador.my_page.application.CheckAmbassadorStatusUseCase;
import com.silicon2.admin.ambassador.my_page.application.GenerateSnsLinkUseCase;
import com.silicon2.admin.ambassador.my_page.application.SubmitReviewUseCase;
import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewRequest;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.doNothing;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(AmbassadorMyPageController.class)
@DisplayName("AmbassadorMyPageController 테스트")
class AmbassadorMyPageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private CheckAmbassadorStatusUseCase checkAmbassadorStatusUseCase;

    @MockBean
    private SubmitReviewUseCase submitReviewUseCase;

    @MockBean
    private GenerateSnsLinkUseCase generateSnsLinkUseCase;

    @Test
    @DisplayName("GET /ambassador/my-page/status - 앰버서더 상태 조회 성공")
    void checkStatus_returnsOk() throws Exception {
        // given
        Long memberId = 100L;
        AmbassadorStatusResponse response = AmbassadorStatusResponse.builder()
                .memberId(memberId)
                .status(AmbassadorStatus.ACTIVE)
                .trackingCode("AMB001")
                .canAccess(true)
                .build();

        given(checkAmbassadorStatusUseCase.execute(eq(memberId)))
                .willReturn(response);

        // when & then
        mockMvc.perform(get("/ambassador/my-page/status")
                        .param("memberId", memberId.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.memberId").value(memberId))
                .andExpect(jsonPath("$.status").value("ACTIVE"))
                .andExpect(jsonPath("$.trackingCode").value("AMB001"))
                .andExpect(jsonPath("$.canAccess").value(true));
    }

    @Test
    @DisplayName("POST /ambassador/my-page/review - 리뷰 제출 성공")
    void submitReview_returnsOk() throws Exception {
        // given
        SubmitReviewRequest request = SubmitReviewRequest.builder()
                .memberId(100L)
                .campaignId(1L)
                .reviewContent("Great product!")
                .imageUrls(Arrays.asList("img1.jpg", "img2.jpg"))
                .build();

        doNothing().when(submitReviewUseCase).execute(any(SubmitReviewRequest.class));

        // when & then
        mockMvc.perform(post("/ambassador/my-page/review")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("POST /ambassador/my-page/sns-link - SNS 링크 생성 성공")
    void generateSnsLink_returnsOk() throws Exception {
        // given
        GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                .memberId(100L)
                .campaignId(1L)
                .snsType("INSTAGRAM")
                .build();

        GenerateSnsLinkResponse response = GenerateSnsLinkResponse.builder()
                .shareUrl("https://example.com/campaign/1?ref=AMB001")
                .trackingCode("AMB001")
                .build();

        given(generateSnsLinkUseCase.execute(any(GenerateSnsLinkRequest.class)))
                .willReturn(response);

        // when & then
        mockMvc.perform(post("/ambassador/my-page/sns-link")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.shareUrl").value("https://example.com/campaign/1?ref=AMB001"))
                .andExpect(jsonPath("$.trackingCode").value("AMB001"));
    }
}
