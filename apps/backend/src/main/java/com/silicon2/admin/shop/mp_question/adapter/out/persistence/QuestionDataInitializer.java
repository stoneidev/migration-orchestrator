package com.silicon2.admin.shop.mp_question.adapter.out.persistence;

import com.silicon2.admin.shop.mp_question.domain.Question;
import com.silicon2.admin.shop.mp_question.domain.QuestionRepository;
import com.silicon2.admin.shop.mp_question.domain.QuestionStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
@Profile("nomysql")
@RequiredArgsConstructor
public class QuestionDataInitializer implements CommandLineRunner {

    private final QuestionRepository questionRepository;

    @Override
    public void run(String... args) {
        if (questionRepository.count() > 0) {
            return;
        }

        Question q1 = new Question();
        q1.setProductName("Korean Beauty Essence Set");
        q1.setCategory("Beauty");
        q1.setQuestionText("Is this suitable for sensitive skin? I have very dry and sensitive skin.");
        q1.setAnswerText("Yes, this product is hypoallergenic and suitable for sensitive skin types.");
        q1.setUserId("user1");
        q1.setUserName("Sarah Kim");
        q1.setCreatedAt(LocalDateTime.of(2026, 5, 20, 10, 30));
        q1.setStatus(QuestionStatus.ANSWERED);

        Question q2 = new Question();
        q2.setProductName("Premium Green Tea");
        q2.setCategory("Food");
        q2.setQuestionText("What is the expiration date for this product?");
        q2.setUserId("user1");
        q2.setUserName("Sarah Kim");
        q2.setCreatedAt(LocalDateTime.of(2026, 5, 18, 14, 20));
        q2.setStatus(QuestionStatus.UNANSWERED);

        Question q3 = new Question();
        q3.setProductName("Wireless Earbuds");
        q3.setCategory("Electronics");
        q3.setQuestionText("Does this come with a warranty?");
        q3.setAnswerText("Yes, it comes with a 1-year manufacturer warranty.");
        q3.setUserId("user1");
        q3.setUserName("Sarah Kim");
        q3.setCreatedAt(LocalDateTime.of(2026, 4, 28, 9, 15));
        q3.setStatus(QuestionStatus.ANSWERED);

        questionRepository.save(q1);
        questionRepository.save(q2);
        questionRepository.save(q3);
    }
}
