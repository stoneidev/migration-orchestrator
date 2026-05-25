import { Question } from './types';

export const mockQuestions: Question[] = [
  {
    id: '1',
    productName: 'Korean Beauty Essence Set',
    category: 'Beauty',
    questionText: 'Is this suitable for sensitive skin? I have very dry and sensitive skin.',
    answerText: 'Yes, this product is hypoallergenic and suitable for sensitive skin types.',
    userId: 'user1',
    userName: 'Sarah Kim',
    createdAt: '2026-05-20T10:30:00Z',
    status: 'answered'
  },
  {
    id: '2',
    productName: 'Premium Green Tea',
    category: 'Food',
    questionText: 'What is the expiration date for this product?',
    userId: 'user1',
    userName: 'Sarah Kim',
    createdAt: '2026-05-18T14:20:00Z',
    status: 'unanswered'
  },
  {
    id: '3',
    productName: 'Wireless Earbuds',
    category: 'Electronics',
    questionText: 'Does this come with a warranty?',
    answerText: 'Yes, it comes with a 1-year manufacturer warranty.',
    userId: 'user1',
    userName: 'Sarah Kim',
    createdAt: '2026-04-28T09:15:00Z',
    status: 'answered'
  }
];
