import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-private-navbar',
  templateUrl: './private-navbar.component.html',
  styleUrl: './private-navbar.component.css'
})
export class PrivateNavbarComponent {
  isDropdownOpen = false;

  constructor(private route: Router, public authService: AuthService) {

  }
  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  logout(): void {
    this.authService.logout();
  }
  // logout() {
  //   this.route.navigate(['']);
  // }
}
