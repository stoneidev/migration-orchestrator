package com.silicon2.admin.ambassador.my_page.adapter.in.web;

import com.silicon2.admin.ambassador.my_page.application.CheckAmbassadorStatusUseCase;
import com.silicon2.admin.ambassador.my_page.application.GenerateSnsLinkUseCase;
import com.silicon2.admin.ambassador.my_page.application.SubmitReviewUseCase;
import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ambassador/my-page")
@RequiredArgsConstructor
public class AmbassadorMyPageController {

    private final CheckAmbassadorStatusUseCase checkAmbassadorStatusUseCase;
    private final SubmitReviewUseCase submitReviewUseCase;
    private final GenerateSnsLinkUseCase generateSnsLinkUseCase;

    @GetMapping("/status")
    public ResponseEntity<AmbassadorStatusResponse> checkStatus(@RequestParam Long memberId) {
        AmbassadorStatusResponse response = checkAmbassadorStatusUseCase.execute(memberId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/review")
    public ResponseEntity<Void> submitReview(@RequestBody SubmitReviewRequest request) {
        submitReviewUseCase.execute(request);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/sns-link")
    public ResponseEntity<GenerateSnsLinkResponse> generateSnsLink(@RequestBody GenerateSnsLinkRequest request) {
        GenerateSnsLinkResponse response = generateSnsLinkUseCase.execute(request);
        return ResponseEntity.ok(response);
    }
}
