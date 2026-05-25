package com.silicon2.admin.shop.mp_question.adapter.in.web;

import com.silicon2.admin.shop.mp_question.application.DeleteQuestionUseCase;
import com.silicon2.admin.shop.mp_question.application.ListQuestionsUseCase;
import com.silicon2.admin.shop.mp_question.application.SubmitQuestionUseCase;
import com.silicon2.admin.shop.mp_question.application.ViewMyQuestionsUseCase;
import com.silicon2.admin.shop.mp_question.application.dto.QuestionRequest;
import com.silicon2.admin.shop.mp_question.application.dto.QuestionResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/shop/mp-question")
@RequiredArgsConstructor
public class QuestionController {

    private final ListQuestionsUseCase listQuestionsUseCase;
    private final ViewMyQuestionsUseCase viewMyQuestionsUseCase;
    private final SubmitQuestionUseCase submitQuestionUseCase;
    private final DeleteQuestionUseCase deleteQuestionUseCase;

    @GetMapping("/list")
    public ResponseEntity<List<QuestionResponse>> listAllQuestions(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String dateFrom,
            @RequestParam(required = false) String dateTo,
            @RequestParam(required = false) String status
    ) {
        List<QuestionResponse> questions = listQuestionsUseCase.execute(category, dateFrom, dateTo, status);
        return ResponseEntity.ok(questions);
    }

    @GetMapping("/my-questions")
    public ResponseEntity<List<QuestionResponse>> viewMyQuestions(@RequestParam String userId) {
        List<QuestionResponse> questions = viewMyQuestionsUseCase.execute(userId);
        return ResponseEntity.ok(questions);
    }

    @PostMapping("/submit")
    public ResponseEntity<QuestionResponse> submitQuestion(@RequestBody QuestionRequest request) {
        QuestionResponse response = submitQuestionUseCase.execute(request);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{questionId}")
    public ResponseEntity<Void> deleteQuestion(@PathVariable Long questionId) {
        deleteQuestionUseCase.execute(questionId);
        return ResponseEntity.ok().build();
    }
}
