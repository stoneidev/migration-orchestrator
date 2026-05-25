import { AlertCloseParams } from './types';

export const mockAlertData: AlertCloseParams = {
  message: '정상적으로 처리되었습니다.',
  isError: false,
};

export const mockErrorData: AlertCloseParams = {
  message: '필수 항목이 입력되지 않았습니다.\\n다시 확인해 주세요.',
  isError: true,
};

export const mockSuccessWithMultiline: AlertCloseParams = {
  message: '저장이 완료되었습니다.\\n이전 화면으로 돌아갑니다.',
  isError: false,
};

export const mockAccessError: AlertCloseParams = {
  message: '접근 권한이 없습니다.',
  isError: true,
};
