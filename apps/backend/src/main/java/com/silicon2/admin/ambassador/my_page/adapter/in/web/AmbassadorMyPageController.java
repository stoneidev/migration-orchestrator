package com.silicon2.admin.ambassador.my_page.adapter.in.web;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.ReviewSubmitRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.ReviewSubmitResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.SnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.SnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.application.usecase.CheckAmbassadorStatusUseCase;
import com.silicon2.admin.ambassador.my_page.application.usecase.GenerateSnsLinkUseCase;
import com.silicon2.admin.ambassador.my_page.application.usecase.SubmitReviewUseCase;
import com.silicon2.admin.common.response.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ambassador/my-page")
@RequiredArgsConstructor
public class AmbassadorMyPageController {

    private final CheckAmbassadorStatusUseCase checkAmbassadorStatusUseCase;
    private final SubmitReviewUseCase submitReviewUseCase;
    private final GenerateSnsLinkUseCase generateSnsLinkUseCase;

    @GetMapping("/status/{ambassadorId}")
    public ApiResponse<AmbassadorStatusResponse> checkAmbassadorStatus(
            @PathVariable Long ambassadorId) {
        AmbassadorStatusResponse response = checkAmbassadorStatusUseCase.execute(ambassadorId);
        return ApiResponse.success(response);
    }

    @PostMapping("/review/{ambassadorId}")
    public ApiResponse<ReviewSubmitResponse> submitReview(
            @PathVariable Long ambassadorId,
            @RequestBody ReviewSubmitRequest request) {
        ReviewSubmitResponse response = submitReviewUseCase.execute(ambassadorId, request);
        return ApiResponse.success(response);
    }

    @PostMapping("/sns-link/{ambassadorId}")
    public ApiResponse<SnsLinkResponse> generateSnsLink(
            @PathVariable Long ambassadorId,
            @RequestBody SnsLinkRequest request) {
        SnsLinkResponse response = generateSnsLinkUseCase.execute(ambassadorId, request);
        return ApiResponse.success(response);
    }
}
