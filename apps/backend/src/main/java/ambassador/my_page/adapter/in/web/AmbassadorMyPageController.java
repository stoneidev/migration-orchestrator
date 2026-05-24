package com.silicon2.admin.ambassador.my_page.adapter.in.web;

import com.silicon2.admin.ambassador.my_page.application.dto.*;
import com.silicon2.admin.ambassador.my_page.application.usecase.CheckAmbassadorStatusUseCase;
import com.silicon2.admin.ambassador.my_page.application.usecase.GenerateSnsLinkUseCase;
import com.silicon2.admin.ambassador.my_page.application.usecase.SubmitReviewUseCase;
import com.silicon2.admin.common.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ambassador/my-page")
@RequiredArgsConstructor
public class AmbassadorMyPageController {

    private final CheckAmbassadorStatusUseCase checkAmbassadorStatusUseCase;
    private final SubmitReviewUseCase submitReviewUseCase;
    private final GenerateSnsLinkUseCase generateSnsLinkUseCase;

    @GetMapping("/status")
    public ResponseEntity<ApiResponse<AmbassadorStatusResponse>> checkAmbassadorStatus(
            @RequestParam Long memberId) {
        try {
            AmbassadorStatusResponse response = checkAmbassadorStatusUseCase.execute(memberId);
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(ApiResponse.error(e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(403)
                .body(ApiResponse.error(e.getMessage()));
        }
    }

    @PostMapping("/review")
    public ResponseEntity<ApiResponse<SubmitReviewResponse>> submitReview(
            @RequestParam Long memberId,
            @RequestBody SubmitReviewRequest request) {
        try {
            SubmitReviewResponse response = submitReviewUseCase.execute(memberId, request);
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(ApiResponse.error(e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(400)
                .body(ApiResponse.error(e.getMessage()));
        }
    }

    @PostMapping("/sns-link")
    public ResponseEntity<ApiResponse<GenerateSnsLinkResponse>> generateSnsLink(
            @RequestParam Long memberId,
            @RequestBody GenerateSnsLinkRequest request) {
        try {
            GenerateSnsLinkResponse response = generateSnsLinkUseCase.execute(memberId, request);
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(ApiResponse.error(e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(400)
                .body(ApiResponse.error(e.getMessage()));
        }
    }
}
