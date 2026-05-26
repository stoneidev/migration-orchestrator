package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionRequest;
import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.model.Question;
import com.silicon2.admin.shop.mp_question.domain.model.QuestionStatus;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import static org.assertj.core.api.BDDAssertions.then;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@BddTest
@DisplayName("SubmitQuestionUseCase")
class SubmitQuestionUseCaseTest {

    @Mock
    private QuestionRepository questionRepository;

    @InjectMocks
    private SubmitQuestionUseCase useCase;

    @Nested
    @DisplayName("질문 제출 시")
    class WhenSubmittingQuestion {

        @Test
        @DisplayName("UNANSWERED 상태로 질문을 저장한다")
        void shouldSaveQuestionAsUnanswered() throws Exception {
            QuestionRequest request = new QuestionRequest(
                    "Serum", "Beauty", "Is this vegan?", "user1", "Kim"
            );

            Bdd.given(() -> given(questionRepository.save(any(Question.class)))
                    .willAnswer(invocation -> {
                        Question q = invocation.getArgument(0);
                        q.setId(1L);
                        return q;
                    }));

            QuestionResponse response = Bdd.when(() -> useCase.execute(request));

            Bdd.then(() -> {
                then(response.getProductName()).isEqualTo("Serum");
                then(response.getStatus()).isEqualTo(QuestionStatus.UNANSWERED);

                ArgumentCaptor<Question> captor = ArgumentCaptor.forClass(Question.class);
                verify(questionRepository).save(captor.capture());
                then(captor.getValue().getUserId()).isEqualTo("user1");
                then(captor.getValue().getCreatedAt()).isNotNull();
            });
        }
    }
}
