package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.model.Question;
import com.silicon2.admin.shop.mp_question.domain.model.QuestionStatus;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.BDDAssertions.then;
import static org.mockito.BDDMockito.given;

@BddTest
@DisplayName("ListQuestionsUseCase")
class ListQuestionsUseCaseTest {

    @Mock
    private QuestionRepository questionRepository;

    @InjectMocks
    private ListQuestionsUseCase useCase;

    @Nested
    @DisplayName("질문 목록 조회 시")
    class WhenListingQuestions {

        @Test
        @DisplayName("카테고리와 상태 조건에 맞는 질문만 반환한다")
        void shouldFilterByCategoryAndStatus() {
            Bdd.given(() -> given(questionRepository.findAll()).willReturn(List.of(
                    question("Serum", "Beauty", QuestionStatus.UNANSWERED, "05/15/2026"),
                    question("Tea", "Food", QuestionStatus.ANSWERED, "05/15/2026")
            )));

            List<QuestionResponse> responses = Bdd.when(() ->
                    useCase.execute("Beauty", null, null, "UNANSWERED")
            );

            Bdd.then(() -> {
                then(responses).hasSize(1);
                then(responses.get(0).getProductName()).isEqualTo("Serum");
            });
        }

        @Test
        @DisplayName("날짜 범위 조건에 맞는 질문만 반환한다")
        void shouldFilterByDateRange() {
            Bdd.given(() -> given(questionRepository.findAll()).willReturn(List.of(
                    question("Serum", "Beauty", QuestionStatus.UNANSWERED, "05/15/2026"),
                    question("Cream", "Beauty", QuestionStatus.UNANSWERED, "04/01/2026")
            )));

            List<QuestionResponse> responses = Bdd.when(() ->
                    useCase.execute(null, "05/01/2026", "05/31/2026", null)
            );

            Bdd.then(() -> then(responses).hasSize(1));
        }
    }

    private Question question(String productName, String category, QuestionStatus status, String date) {
        Question question = Question.create(productName, category, "question?", "user1", "Kim");
        question.setStatus(status);
        String[] parts = date.split("/");
        question.setCreatedAt(LocalDateTime.of(
                Integer.parseInt(parts[2]),
                Integer.parseInt(parts[0]),
                Integer.parseInt(parts[1]),
                10, 0
        ));
        return question;
    }
}
