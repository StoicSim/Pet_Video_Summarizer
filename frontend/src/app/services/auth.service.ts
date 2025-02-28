// auth.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000';
  private loggedIn = new BehaviorSubject<boolean>(false);
  private currentUserSubject = new BehaviorSubject<any>(null);

  constructor(
    private router: Router,
    private http: HttpClient
  ) {
    // Check if user was previously logged in
    const token = localStorage.getItem('token');
    if (token) {
      this.loggedIn.next(true);
      // Also restore user details if available
      const userData = JSON.parse(localStorage.getItem('userData') || '{}');
      this.currentUserSubject.next(userData);
    }
  }

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, {
      username,
      password
    }).pipe(
      tap(response => {
        // Store token and user data
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('userData', JSON.stringify({
          id: response.user_id,
          username: response.username
        }));

        // Update observables
        this.loggedIn.next(true);
        this.currentUserSubject.next({
          id: response.user_id,
          username: response.username
        });

        // Navigate to home page
        this.router.navigate(['/']);
      }),
      catchError(this.handleError)
    );
  }

  logout(): void {
    // Clear stored data
    localStorage.removeItem('token');
    localStorage.removeItem('userData');

    // Update observables
    this.loggedIn.next(false);
    this.currentUserSubject.next(null);

    // Navigate to home
    this.router.navigate(['/']);
  }

  isLoggedIn(): boolean {
    return this.loggedIn.value;
  }

  getUserName(): string {
    const userData = this.currentUserSubject.value;
    return userData ? userData.username : 'User';
  }

  getLoggedInStatus() {
    return this.loggedIn.asObservable();
  }

  getCurrentUser() {
    return this.currentUserSubject.asObservable();
  }

  // Get the token for authenticated requests
  getToken(): string | null {
    return localStorage.getItem('token');
  }


  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.status === 401) {
        errorMessage = 'Invalid username or password';
      } else {
        errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
      }
    }
    return throwError(() => new Error(errorMessage));
  }
}