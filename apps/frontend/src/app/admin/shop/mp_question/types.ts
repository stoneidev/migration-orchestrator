export interface Question {
  id: string;
  productName: string;
  category: string;
  questionText: string;
  answerText?: string;
  userId: string;
  userName: string;
  createdAt: string;
  status: 'answered' | 'unanswered';
}

export type PeriodFilter = '1 Week' | '1 Month' | '3 Month' | 'This Year';
export type CategoryFilter = 'All' | string;
