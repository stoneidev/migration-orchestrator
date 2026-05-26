package com.silicon2.admin.testsupport.bdd;

import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * BDD 스타일 단위 테스트용 메타 어노테이션.
 * MockitoExtension을 활성화하여 BDDMockito(given/then) 사용을 지원한다.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@ExtendWith(MockitoExtension.class)
public @interface BddTest {
}
