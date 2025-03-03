import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../../models/user.model';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {
  user: User = new User('', '', '', '');
  errorMessage: string | null = null;

  constructor(private router: Router, private userService: UserService) { }

  onSignUp() {
    this.userService.registerUser(this.user).subscribe(
      response => {
        if (response.auth_url) {
          // Redirect to Google auth
          window.location.href = response.auth_url;
        } else {
          // Fall back to normal login flow
          this.router.navigate(['/login']);
        }
      },
      error => {
        this.errorMessage = error.error.detail || 'Registration failed';
      }
    );
  }
}
