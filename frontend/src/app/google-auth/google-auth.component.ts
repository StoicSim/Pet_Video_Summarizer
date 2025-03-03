import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GoogleDriveService } from '../services/google-drive.service';

@Component({
  selector: 'app-google-auth',
  templateUrl: './google-auth.component.html',
  styleUrls: ['./google-auth.component.css']
})
export class GoogleAuthComponent implements OnInit {
  userId: string | null = null;
  authUrl: string | null = null;
  isLoading = true;
  errorMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private googleDriveService: GoogleDriveService
  ) { }

  ngOnInit(): void {
    this.userId = this.route.snapshot.queryParamMap.get('user_id');

    if (this.userId) {
      this.getGoogleAuthUrl();
    } else {
      this.errorMessage = 'User ID is missing. Cannot proceed with Google authorization.';
      this.isLoading = false;
    }
  }

  getGoogleAuthUrl(): void {
    this.googleDriveService.getAuthUrl().subscribe(
      response => {
        this.authUrl = response.auth_url;
        this.isLoading = false;
      },
      error => {
        this.errorMessage = 'Failed to get Google authorization URL.';
        this.isLoading = false;
        console.error('Error getting auth URL:', error);
      }
    );
  }

  continueWithoutGoogle(): void {
    // Redirect to login page if user doesn't want to connect Google Drive
    window.location.href = '/login';
  }
}
