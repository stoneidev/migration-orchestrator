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
import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.willDoNothing;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(AmbassadorMyPageController.class)
@DisplayName("AmbassadorMyPageController")
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

    @Nested
    @DisplayName("GET /ambassador/my-page/status")
    class WhenCheckingStatus {

        @Test
        @DisplayName("앰버서더 상태를 조회하면 200과 상태 데이터를 반환한다")
        void shouldReturnAmbassadorStatus() throws Exception {
            Bdd.given(() -> given(checkAmbassadorStatusUseCase.execute(eq(100L)))
                    .willReturn(AmbassadorStatusResponse.builder()
                            .memberId(100L)
                            .status(AmbassadorStatus.ACTIVE)
                            .trackingCode("AMB001")
                            .canAccess(true)
                            .build()));

            Bdd.when(() -> mockMvc.perform(get("/ambassador/my-page/status")
                            .param("memberId", "100")))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.status").value("ACTIVE"))
                    .andExpect(jsonPath("$.canAccess").value(true));
        }
    }

    @Nested
    @DisplayName("POST /ambassador/my-page/review")
    class WhenSubmittingReview {

        @Test
        @DisplayName("리뷰를 제출하면 200을 반환한다")
        void shouldSubmitReview() throws Exception {
            SubmitReviewRequest request = SubmitReviewRequest.builder()
                    .memberId(100L)
                    .campaignId(1L)
                    .reviewContent("Great product!")
                    .imageUrls(List.of("img1.jpg"))
                    .build();

            Bdd.given(() -> willDoNothing().given(submitReviewUseCase)
                    .execute(any(SubmitReviewRequest.class)));

            Bdd.when(() -> mockMvc.perform(post("/ambassador/my-page/review")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request))))
                    .andExpect(status().isOk());
        }
    }

    @Nested
    @DisplayName("POST /ambassador/my-page/sns-link")
    class WhenGeneratingSnsLink {

        @Test
        @DisplayName("SNS 링크를 생성하면 200과 링크 데이터를 반환한다")
        void shouldGenerateSnsLink() throws Exception {
            GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                    .memberId(100L)
                    .campaignId(1L)
                    .snsType("INSTAGRAM")
                    .build();

            Bdd.given(() -> given(generateSnsLinkUseCase.execute(any(GenerateSnsLinkRequest.class)))
                    .willReturn(GenerateSnsLinkResponse.builder()
                            .shareUrl("https://example.com/campaign/1?ref=AMB001")
                            .trackingCode("AMB001")
                            .build()));

            Bdd.when(() -> mockMvc.perform(post("/ambassador/my-page/sns-link")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request))))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.trackingCode").value("AMB001"));
        }
    }
}
