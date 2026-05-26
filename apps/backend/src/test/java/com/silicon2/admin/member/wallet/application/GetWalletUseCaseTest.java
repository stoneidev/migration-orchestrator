package com.silicon2.admin.member.wallet.application;

import com.silicon2.admin.member.wallet.application.dto.WalletResponse;
import com.silicon2.admin.member.wallet.domain.model.Member;
import com.silicon2.admin.member.wallet.domain.repository.MemberRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.then;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;
import static org.mockito.BDDMockito.given;

@BddTest
@DisplayName("GetWalletUseCase")
class GetWalletUseCaseTest {

    @Mock
    private MemberRepository memberRepository;

    @InjectMocks
    private GetWalletUseCase useCase;

    @Nested
    @DisplayName("지갑 조회 시")
    class WhenGettingWallet {

        @Test
        @DisplayName("존재하는 회원의 포인트와 쿠폰 정보를 반환한다")
        void shouldReturnWalletData() {
            Member member = Member.builder()
                    .mbId("test_member")
                    .mbPoint(150)
                    .mbName("Test User")
                    .mbEmail("test@stylekorean.com")
                    .hasUsedCoupon(true)
                    .couponCount(3)
                    .build();

            Bdd.given(() -> given(memberRepository.findByMbId("test_member"))
                    .willReturn(Optional.of(member)));

            WalletResponse response = Bdd.when(() -> useCase.execute("test_member"));

            Bdd.then(() -> {
                then(response.getSuccess()).isTrue();
                then(response.getData().getMember().getMbPoint()).isEqualTo(150);
                then(response.getData().getCouponStatus().getCouponCount()).isEqualTo(3);
            });
        }

        @Test
        @DisplayName("존재하지 않는 회원이면 예외를 발생시킨다")
        void shouldThrowWhenMemberNotFound() {
            Bdd.given(() -> given(memberRepository.findByMbId("unknown"))
                    .willReturn(Optional.empty()));

            Bdd.then(() -> thenThrownBy(() -> useCase.execute("unknown"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Member not found"));
        }
    }
}
