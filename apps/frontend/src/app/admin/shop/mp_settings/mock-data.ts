import { AccountSettings } from './types';

export const mockAccountSettings: AccountSettings = {
  firstName: 'First Name',
  lastName: 'Last Name',
  emailId: 'stoneidev@gmail.com',
  dateOfBirth: {
    month: 1,
    day: 1,
    year: 1935,
  },
};

export const months = [
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 4, label: '4' },
  { value: 5, label: '5' },
  { value: 6, label: '6' },
  { value: 7, label: '7' },
  { value: 8, label: '8' },
  { value: 9, label: '9' },
  { value: 10, label: '10' },
  { value: 11, label: '11' },
  { value: 12, label: '12' },
];

export const days = Array.from({ length: 31 }, (_, i) => ({
  value: i + 1,
  label: `${i + 1}`,
}));

export const years = Array.from({ length: 100 }, (_, i) => ({
  value: 2024 - i,
  label: `${2024 - i}`,
}));
