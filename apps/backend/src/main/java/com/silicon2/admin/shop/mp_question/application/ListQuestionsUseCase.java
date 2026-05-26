package com.silicon2.admin.shop.mp_question.application;

import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import com.silicon2.admin.shop.mp_question.domain.model.Question;
import com.silicon2.admin.shop.mp_question.domain.repository.QuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ListQuestionsUseCase {

    private final QuestionRepository questionRepository;

    @Transactional(readOnly = true)
    public List<QuestionResponse> execute(String category, String dateFrom, String dateTo, String status) {
        List<Question> questions = questionRepository.findAll();

        return questions.stream()
            .filter(q -> category == null || category.isEmpty() || category.equals("All") || q.getCategory().equals(category))
            .filter(q -> filterByDateRange(q, dateFrom, dateTo))
            .filter(q -> status == null || status.isEmpty() || q.getStatus().name().equals(status))
            .map(QuestionResponse::from)
            .collect(Collectors.toList());
    }

    private boolean filterByDateRange(Question question, String dateFrom, String dateTo) {
        if (dateFrom == null && dateTo == null) {
            return true;
        }

        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/dd/yyyy");
            LocalDateTime questionDate = question.getCreatedAt();

            if (dateFrom != null && !dateFrom.isEmpty()) {
                LocalDate fromDate = LocalDate.parse(dateFrom, formatter);
                if (questionDate.toLocalDate().isBefore(fromDate)) {
                    return false;
                }
            }

            if (dateTo != null && !dateTo.isEmpty()) {
                LocalDate toDate = LocalDate.parse(dateTo, formatter);
                if (questionDate.toLocalDate().isAfter(toDate)) {
                    return false;
                }
            }

            return true;
        } catch (Exception e) {
            return true;
        }
    }
}
