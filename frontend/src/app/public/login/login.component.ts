import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  rememberMe: boolean = false;
  loginError: string = '';

  constructor(
    private router: Router,
    private authService: AuthService
  ) { }

  onClick() {
    // Get values directly from the DOM elements since you're not using reactive forms
    const emailElement = document.getElementById('email') as HTMLInputElement;
    const passwordElement = document.getElementById('password') as HTMLInputElement;
    const rememberMeElement = document.getElementById('remember-me') as HTMLInputElement;

    this.email = emailElement?.value || '';
    this.password = passwordElement?.value || '';
    this.rememberMe = rememberMeElement?.checked || false;

    // Basic validation
    if (!this.email || !this.password) {
      this.loginError = 'Please enter both email and password';
      return;
    }

    // Call the auth service for dummy login
    this.authService.dummyLogin(this.email, this.password);

    // No need to navigate here as the AuthService will handle navigation
  }
}