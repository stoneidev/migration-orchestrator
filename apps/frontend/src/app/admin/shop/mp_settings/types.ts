export interface AccountSettings {
  firstName: string;
  lastName: string;
  emailId: string;
  dateOfBirth: {
    month: number;
    day: number;
    year: number;
  };
}

export interface UpdateAccountRequest {
  firstName?: string;
  lastName?: string;
  dateOfBirth?: {
    month: number;
    day: number;
    year: number;
  };
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

export interface DeleteAccountRequest {
  password: string;
}
