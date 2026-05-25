package com.silicon2.admin.member.wallet.adapter.in.web;

import com.silicon2.admin.member.wallet.application.GetWalletUseCase;
import com.silicon2.admin.member.wallet.application.dto.WalletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/v1/member/wallet")
@RequiredArgsConstructor
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:3001"})
public class WalletController {

    private final GetWalletUseCase getWalletUseCase;

    @GetMapping
    public ResponseEntity<WalletResponse> getWallet(
            @RequestParam(required = false, defaultValue = "test_member") String mbId
    ) {
        WalletResponse response = getWalletUseCase.execute(mbId);
        return ResponseEntity.ok(response);
    }
}
