import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { VideoService } from '../../services/video.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  isLoggedIn = false;
  userEmail = '';
  videoUrl = '';
  isUploading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private authService: AuthService,
    private videoService: VideoService,
    private router: Router
  ) { }

  ngOnInit(): void {
    // Check initial login status
    this.isLoggedIn = this.authService.isLoggedIn();

    // Subscribe to login status changes
    this.authService.getLoggedInStatus().subscribe(status => {
      this.isLoggedIn = status;
    });
  }

  onUpload(): void {
    this.resetMessages();
    this.isUploading = true;

    try {
      // Call video service to upload
      this.videoService.uploadVideo(this.videoUrl, this.isLoggedIn ? undefined : this.userEmail)
        .subscribe({
          next: (response) => {
            this.isUploading = false;
            this.successMessage = 'Video uploaded successfully!';
            this.videoUrl = '';
            if (!this.isLoggedIn) {
              this.userEmail = '';
            }

            // Optionally navigate to a results page or dashboard
            // this.router.navigate(['/videos', response.video_id]);
          },
          error: (error) => {
            this.isUploading = false;
            this.errorMessage = error.error?.detail || 'Failed to upload video. Please try again.';
          }
        });
    } catch (error: any) {
      this.isUploading = false;
      this.errorMessage = error.message || 'An error occurred while uploading.';
    }
  }

  canUpload(): boolean {
    if (this.isLoggedIn) {
      return !!this.videoUrl; // Just need video URL if logged in
    } else {
      return !!this.videoUrl && !!this.userEmail && this.userEmail.includes('@'); // Need both if not logged in
    }
  }

  private resetMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }
}