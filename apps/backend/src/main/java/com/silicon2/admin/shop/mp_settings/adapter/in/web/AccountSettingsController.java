package com.silicon2.admin.shop.mp_settings.adapter.in.web;

import com.silicon2.admin.shop.mp_settings.application.DeleteAccountUseCase;
import com.silicon2.admin.shop.mp_settings.application.GetAccountSettingsUseCase;
import com.silicon2.admin.shop.mp_settings.application.UpdateAccountSettingsUseCase;
import com.silicon2.admin.shop.mp_settings.application.dto.AccountSettingsResponse;
import com.silicon2.admin.shop.mp_settings.application.dto.DeleteAccountRequest;
import com.silicon2.admin.shop.mp_settings.application.dto.UpdateAccountSettingsRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/shop/mp-settings")
@RequiredArgsConstructor
public class AccountSettingsController {

    private final GetAccountSettingsUseCase getAccountSettingsUseCase;
    private final UpdateAccountSettingsUseCase updateAccountSettingsUseCase;
    private final DeleteAccountUseCase deleteAccountUseCase;

    @GetMapping
    public ResponseEntity<AccountSettingsResponse> getAccountSettings(@RequestParam Long memberId) {
        AccountSettingsResponse response = getAccountSettingsUseCase.execute(memberId);
        return ResponseEntity.ok(response);
    }

    @PostMapping
    public ResponseEntity<Void> updateAccountSettings(@RequestBody UpdateAccountSettingsRequest request) {
        updateAccountSettingsUseCase.execute(request);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/delete")
    public ResponseEntity<Void> deleteAccount(@RequestBody DeleteAccountRequest request) {
        deleteAccountUseCase.execute(request);
        return ResponseEntity.ok().build();
    }
}
