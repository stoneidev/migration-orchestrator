package com.silicon2.admin.shop.mp_profile.adapter.in.web;

import com.silicon2.admin.shop.mp_profile.application.GetBeautyProfileUseCase;
import com.silicon2.admin.shop.mp_profile.application.SaveBeautyProfileUseCase;
import com.silicon2.admin.shop.mp_profile.application.dto.ApiResponse;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/v1/shop/profile")
@RequiredArgsConstructor
public class BeautyProfileController {

    private final GetBeautyProfileUseCase getBeautyProfileUseCase;
    private final SaveBeautyProfileUseCase saveBeautyProfileUseCase;

    @GetMapping
    public ResponseEntity<ApiResponse<BeautyProfileResponse>> getBeautyProfile(
            @RequestParam(defaultValue = "user123") String userId
    ) {
        BeautyProfileResponse profile = getBeautyProfileUseCase.execute(userId);
        if (profile == null) {
            return ResponseEntity.ok(ApiResponse.success(null));
        }
        return ResponseEntity.ok(ApiResponse.success(profile));
    }

    @PostMapping
    public ResponseEntity<ApiResponse<BeautyProfileResponse>> createOrUpdateBeautyProfile(
            @RequestParam(defaultValue = "user123") String userId,
            @RequestBody BeautyProfileRequest request
    ) {
        BeautyProfileResponse profile = saveBeautyProfileUseCase.execute(userId, request);
        return ResponseEntity.ok(ApiResponse.success(profile));
    }
}
