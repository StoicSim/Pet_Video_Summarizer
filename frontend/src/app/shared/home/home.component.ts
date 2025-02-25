import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service'; // Adjust path if needed

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  isLoggedIn = false;
  userEmail = '';
  videoUrl = '';

  constructor(private authService: AuthService) { }

  ngOnInit(): void {
    // Check initial login status
    this.isLoggedIn = this.authService.isLoggedIn();

    // Subscribe to login status changes
    this.authService.getLoggedInStatus().subscribe(status => {
      this.isLoggedIn = status;
    });
  }

  onUpload(): void {


    // Handle video upload logic here
    console.log('Uploading video:', this.videoUrl);

    // Reset the video URL after upload if needed
    // this.videoUrl = '';
  }

  canUpload(): boolean {
    if (this.isLoggedIn) {
      return !!this.videoUrl; // Just need video URL if logged in
    } else {
      return !!this.videoUrl && !!this.userEmail && this.userEmail.includes('@'); // Need both if not logged in
    }
  }
}