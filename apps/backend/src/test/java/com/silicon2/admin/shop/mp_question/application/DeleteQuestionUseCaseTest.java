package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import static org.mockito.Mockito.verify;

@BddTest
@DisplayName("DeleteQuestionUseCase")
class DeleteQuestionUseCaseTest {

    @Mock
    private QuestionRepository questionRepository;

    @InjectMocks
    private DeleteQuestionUseCase useCase;

    @Nested
    @DisplayName("질문 삭제 시")
    class WhenDeletingQuestion {

        @Test
        @DisplayName("지정된 ID의 질문을 삭제한다")
        void shouldDeleteQuestionById() {
            Long questionId = 42L;

            Bdd.when(() -> useCase.execute(questionId));

            Bdd.then(() -> verify(questionRepository).deleteById(questionId));
        }
    }
}
