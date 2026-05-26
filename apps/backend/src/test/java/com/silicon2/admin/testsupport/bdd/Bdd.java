package com.silicon2.admin.testsupport.bdd;

/**
 * Given-When-Then 단계를 명시적으로 구분하는 BDD 테스트 헬퍼.
 */
public final class Bdd {

    @FunctionalInterface
    public interface Step {
        void run() throws Exception;
    }

    @FunctionalInterface
    public interface StepWithResult<T> {
        T get() throws Exception;
    }

    private Bdd() {
    }

    public static void given(Runnable arrangement) {
        arrangement.run();
    }

    public static <T> T when(StepWithResult<T> action) {
        try {
            return action.get();
        } catch (Exception e) {
            throw new AssertionError(e);
        }
    }

    public static void when(Step action) {
        try {
            action.run();
        } catch (Exception e) {
            throw new AssertionError(e);
        }
    }

    public static void then(Step assertion) {
        try {
            assertion.run();
        } catch (Exception e) {
            throw new AssertionError(e);
        }
    }
}
