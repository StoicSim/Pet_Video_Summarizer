import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AuthService } from './auth.service';

export interface VideoUploadResponse {
  message: string;
  video_id: string;
}

export interface Video {
  unique_id: string;
  user_id: string;
  email: string;
  source_video_link: string;
  source_video_duration: number;
  animal_type: string;
  summary_video_link: string;
  summary_text: string;
  processing_status: string;
  error_message: string;
  created_at: string;
  updated_at: string;
  expiry_date: string;
}

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  // Helper method to get HTTP headers with authentication token

  // In video.service.ts
  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    console.log("Using auth token:", token);

    // Get user data for debugging
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    console.log("Current user ID:", userData.id);

    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }
  // private getAuthHeaders(): HttpHeaders {
  //   const token = this.authService.getToken();
  //   return new HttpHeaders({
  //     'Content-Type': 'application/json',
  //     'Authorization': `Bearer ${token}`
  //   });
  // }

  uploadVideo(videoUrl: string, email?: string): Observable<VideoUploadResponse> {
    // Create the request body
    const body: any = {
      source_video_link: videoUrl
    };

    // If user is not logged in, we need to include the email provided by the user
    if (!this.authService.isLoggedIn()) {
      if (!email) {
        throw new Error('Email is required for anonymous uploads');
      }
      body.email = email;
    }

    const options = this.authService.isLoggedIn()
      ? { headers: this.getAuthHeaders() }
      : {};

    // Return the HTTP post observable
    return this.http.post<VideoUploadResponse>(`${this.apiUrl}/videos/upload`, body, options);
  }

  getUserVideos(): Observable<Video[]> {
    if (!this.authService.isLoggedIn()) {
      console.warn('Attempted to get user videos while not logged in');
      return of([]);
    }

    return this.http.get<Video[]>(
      `${this.apiUrl}/videos/user`,
      { headers: this.getAuthHeaders() }
    ).pipe(
      catchError(error => {
        console.error('Error fetching user videos:', error);
        return of([]);
      })
    );
  }

  getVideoStatus(videoId: string): Observable<Video> {
    const options = this.authService.isLoggedIn()
      ? { headers: this.getAuthHeaders() }
      : {};

    return this.http.get<Video>(`${this.apiUrl}/videos/${videoId}`, options);
  }

  // Method to get today's video for the current user, now including all processing statuses
  getTodayVideo(): Observable<Video | null> {
    if (!this.authService.isLoggedIn()) {
      console.log('User not logged in, cannot fetch today\'s video');
      return of(null);
    }

    return this.getUserVideos().pipe(
      map(videos => {
        if (!videos || videos.length === 0) {
          return null;
        }

        // Filter videos created today
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const todayVideos = videos.filter(video => {
          const videoDate = new Date(video.created_at);
          videoDate.setHours(0, 0, 0, 0);
          return videoDate.getTime() === today.getTime();
          // Removed the processing_status filter to include all videos
        });

        // Sort by creation date (newest first)
        todayVideos.sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );

        // Return the most recent video from today or null if none found
        return todayVideos.length > 0 ? todayVideos[0] : null;
      }),
      catchError(error => {
        console.error('Error fetching today\'s video:', error);
        return of(null);
      })
    );
  }

  getVideosByDate(date: Date): Observable<Video[]> {
    if (!this.authService.isLoggedIn()) {
      console.warn('Attempted to get videos by date while not logged in');
      return of([]);
    }

    // Create a date that preserves the selected date regardless of timezone
    const year = date.getFullYear();
    const month = date.getMonth() + 1; // getMonth() is 0-indexed
    const day = date.getDate();

    // Format as YYYY-MM-DD
    const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

    console.log(`Requesting videos for date: ${formattedDate}`);

    return this.http.get<Video[]>(
      `${this.apiUrl}/videos/date/${formattedDate}`,
      { headers: this.getAuthHeaders() }
    ).pipe(
      catchError(error => {
        console.error('Error fetching videos by date:', error);
        return of([]);
      })
    );
  }

  getFeaturedVideos(): Observable<{ [key: string]: Video | null }> {
    if (!this.authService.isLoggedIn()) {
      console.warn('Attempted to get featured videos while not logged in');
      return of({});
    }

    return this.http.get<{ [key: string]: Video | null }>(
      `${this.apiUrl}/video/featured`,
      { headers: this.getAuthHeaders() }
    ).pipe(
      catchError(error => {
        console.error('Error fetching featured videos:', error);
        return of({});
      })
    );
  }
}


