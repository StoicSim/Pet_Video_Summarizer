import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-private-navbar',
  templateUrl: './private-navbar.component.html',
  styleUrl: './private-navbar.component.css'
})
export class PrivateNavbarComponent {
  isDropdownOpen = false;

  constructor(private route: Router) {

  }
  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  logout() {
    this.route.navigate(['']);
  }
}
