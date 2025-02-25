// auth.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private loggedIn = new BehaviorSubject<boolean>(false);

  constructor(private router: Router) {
    // Check if user was previously logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    this.loggedIn.next(isLoggedIn);
  }

  // Dummy login function - no real authentication
  dummyLogin(username: string, password: string): void {
    // For demo purposes, any non-empty username/password will work
    if (username && password) {
      // Set logged in status
      this.loggedIn.next(true);
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('username', username);

      // Navigate to home page after login
      this.router.navigate(['/']);
    }
  }

  logout(): void {
    this.loggedIn.next(false);
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('username');
    this.router.navigate(['/']);
  }

  isLoggedIn(): boolean {
    return this.loggedIn.value;
  }

  getUserName(): string {
    return localStorage.getItem('username') || 'User';
  }

  getLoggedInStatus() {
    return this.loggedIn.asObservable();
  }
}