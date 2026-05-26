package com.silicon2.admin.shop.mp_question.domain.model;

import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.BDDAssertions.then;

@DisplayName("Question")
class QuestionTest {

    @Nested
    @DisplayName("질문 생성 시")
    class WhenCreating {

        @Test
        @DisplayName("UNANSWERED 상태와 생성일시를 설정한다")
        void shouldCreateWithUnansweredStatus() {
            Question question = Bdd.when(() -> Question.create(
                    "Serum", "Beauty", "Is this vegan?", "user1", "Kim"
            ));

            Bdd.then(() -> {
                then(question.getProductName()).isEqualTo("Serum");
                then(question.getStatus()).isEqualTo(QuestionStatus.UNANSWERED);
                then(question.getCreatedAt()).isNotNull();
            });
        }
    }

    @Nested
    @DisplayName("카테고리 필터 적용 시")
    class WhenMatchingCategory {

        @Test
        @DisplayName("null, 빈 값, All이면 모든 질문에 매칭된다")
        void shouldMatchWildcardCategories() {
            Question question = questionWithCategory("Beauty");

            Bdd.then(() -> {
                then(question.matchesCategory(null)).isTrue();
                then(question.matchesCategory("")).isTrue();
                then(question.matchesCategory("All")).isTrue();
                then(question.matchesCategory("Beauty")).isTrue();
                then(question.matchesCategory("Food")).isFalse();
            });
        }
    }

    @Nested
    @DisplayName("날짜 범위 필터 적용 시")
    class WhenMatchingDateRange {

        @Test
        @DisplayName("지정된 범위 내 질문만 매칭된다")
        void shouldMatchWithinDateRange() {
            Question question = new Question();
            question.setCreatedAt(LocalDateTime.of(2026, 5, 15, 10, 0));

            Bdd.then(() -> {
                then(question.isWithinDateRange(null, null)).isTrue();
                then(question.isWithinDateRange("05/01/2026", "05/31/2026")).isTrue();
                then(question.isWithinDateRange("05/20/2026", null)).isFalse();
                then(question.isWithinDateRange(null, "05/10/2026")).isFalse();
            });
        }
    }

    @Nested
    @DisplayName("검색 조건 적용 시")
    class WhenMatchingSearchCriteria {

        @Test
        @DisplayName("복합 조건에 맞는 질문만 매칭된다")
        void shouldMatchCombinedCriteria() {
            Question question = questionWithCategory("Beauty");
            question.setCreatedAt(LocalDateTime.of(2026, 5, 15, 10, 0));
            question.setStatus(QuestionStatus.UNANSWERED);

            QuestionSearchCriteria matching = new QuestionSearchCriteria(
                    "Beauty", "05/01/2026", "05/31/2026", "UNANSWERED");
            QuestionSearchCriteria nonMatching = new QuestionSearchCriteria("Food", null, null, null);

            Bdd.then(() -> {
                then(question.matchesSearchCriteria(matching)).isTrue();
                then(question.matchesSearchCriteria(nonMatching)).isFalse();
            });
        }
    }

    private Question questionWithCategory(String category) {
        Question question = new Question();
        question.setCategory(category);
        return question;
    }
}
