package com.silicon2.admin.shop.mp_question.adapter.out.persistence;

import com.silicon2.admin.shop.mp_question.domain.Question;
import com.silicon2.admin.shop.mp_question.domain.QuestionRepository;
import com.silicon2.admin.shop.mp_question.domain.QuestionStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component("questionDataInitializer")
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

        Question q4 = new Question();
        q4.setProductName("Korean Ginseng Extract");
        q4.setCategory("Food");
        q4.setQuestionText("How should I store this product?");
        q4.setAnswerText("Store in a cool, dry place away from direct sunlight.");
        q4.setUserId("user2");
        q4.setUserName("John Lee");
        q4.setCreatedAt(LocalDateTime.of(2026, 5, 15, 11, 0));
        q4.setStatus(QuestionStatus.ANSWERED);

        Question q5 = new Question();
        q5.setProductName("Anti-Aging Cream");
        q5.setCategory("Beauty");
        q5.setQuestionText("Can I use this during pregnancy?");
        q5.setUserId("user2");
        q5.setUserName("John Lee");
        q5.setCreatedAt(LocalDateTime.of(2026, 5, 10, 16, 45));
        q5.setStatus(QuestionStatus.UNANSWERED);

        Question q6 = new Question();
        q6.setProductName("Smart Watch Pro");
        q6.setCategory("Electronics");
        q6.setQuestionText("Is it waterproof?");
        q6.setAnswerText("Yes, it has IP68 water resistance rating.");
        q6.setUserId("user3");
        q6.setUserName("Emily Park");
        q6.setCreatedAt(LocalDateTime.of(2026, 5, 22, 13, 30));
        q6.setStatus(QuestionStatus.ANSWERED);

        Question q7 = new Question();
        q7.setProductName("Kimchi Traditional");
        q7.setCategory("Food");
        q7.setQuestionText("Is this product gluten-free?");
        q7.setUserId("user3");
        q7.setUserName("Emily Park");
        q7.setCreatedAt(LocalDateTime.of(2026, 5, 5, 10, 20));
        q7.setStatus(QuestionStatus.UNANSWERED);

        Question q8 = new Question();
        q8.setProductName("Sheet Mask Set");
        q8.setCategory("Beauty");
        q8.setQuestionText("How often should I use this?");
        q8.setAnswerText("We recommend using 2-3 times per week for best results.");
        q8.setUserId("user1");
        q8.setUserName("Sarah Kim");
        q8.setCreatedAt(LocalDateTime.of(2026, 5, 12, 19, 15));
        q8.setStatus(QuestionStatus.ANSWERED);

        Question q9 = new Question();
        q9.setProductName("Bluetooth Speaker");
        q9.setCategory("Electronics");
        q9.setQuestionText("What is the battery life?");
        q9.setUserId("user2");
        q9.setUserName("John Lee");
        q9.setCreatedAt(LocalDateTime.of(2026, 4, 25, 14, 40));
        q9.setStatus(QuestionStatus.UNANSWERED);

        Question q10 = new Question();
        q10.setProductName("Serum Vitamin C");
        q10.setCategory("Beauty");
        q10.setQuestionText("Can I use this with retinol?");
        q10.setAnswerText("It's best to use Vitamin C in the morning and retinol at night.");
        q10.setUserId("user3");
        q10.setUserName("Emily Park");
        q10.setCreatedAt(LocalDateTime.of(2026, 5, 8, 8, 50));
        q10.setStatus(QuestionStatus.ANSWERED);

        questionRepository.save(q1);
        questionRepository.save(q2);
        questionRepository.save(q3);
        questionRepository.save(q4);
        questionRepository.save(q5);
        questionRepository.save(q6);
        questionRepository.save(q7);
        questionRepository.save(q8);
        questionRepository.save(q9);
        questionRepository.save(q10);
    }
}
