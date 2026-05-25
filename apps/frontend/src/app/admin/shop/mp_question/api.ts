import { Question } from './types';
import { mockQuestions } from './mock-data';

const API_BASE_URL = 'http://localhost:8080/api/shop/mp-question';
const API_TIMEOUT = 3000;

interface QuestionFilters {
  category?: string;
  dateFrom?: string;
  dateTo?: string;
  status?: string;
}

export async function fetchQuestions(filters: QuestionFilters): Promise<Question[]> {
  try {
    const params = new URLSearchParams();

    if (filters.category && filters.category !== 'All') {
      params.set('category', filters.category);
    }

    if (filters.dateFrom) {
      params.set('dateFrom', filters.dateFrom);
    }

    if (filters.dateTo) {
      params.set('dateTo', filters.dateTo);
    }

    if (filters.status) {
      params.set('status', filters.status);
    }

    const url = `${API_BASE_URL}/list${params.toString() ? `?${params.toString()}` : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(API_TIMEOUT),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    // Transform backend response to match frontend types
    return data.map((item: any) => {
      // Format date from ISO to MM/DD/YYYY
      let formattedDate = item.createdAt;
      try {
        const date = new Date(item.createdAt);
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const year = date.getFullYear();
        formattedDate = `${month}/${day}/${year}`;
      } catch (e) {
        console.warn('Failed to format date:', item.createdAt);
      }

      return {
        id: item.id.toString(),
        productName: item.productName,
        category: item.category,
        questionText: item.questionText,
        answerText: item.answerText,
        userId: item.userId,
        userName: item.userName,
        createdAt: formattedDate,
        status: item.status.toLowerCase() as 'answered' | 'unanswered',
      };
    });
  } catch (error) {
    console.warn('Failed to fetch from backend, falling back to mock data:', error);

    // Fallback to mock data with client-side filtering
    let filtered = mockQuestions;

    if (filters.category && filters.category !== 'All') {
      filtered = filtered.filter(q => q.category === filters.category);
    }

    if (filters.dateFrom || filters.dateTo) {
      filtered = filtered.filter(q => {
        const qDate = new Date(q.createdAt);
        const fromDate = filters.dateFrom ? new Date(filters.dateFrom) : null;
        const toDate = filters.dateTo ? new Date(filters.dateTo) : null;

        if (fromDate && qDate < fromDate) return false;
        if (toDate && qDate > toDate) return false;

        return true;
      });
    }

    if (filters.status) {
      filtered = filtered.filter(q => q.status.toUpperCase() === filters.status);
    }

    return filtered;
  }
}
