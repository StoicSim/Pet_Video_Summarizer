// video.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface VideoUploadResponse {
  message: string;
  video_id: string;
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

    // Return the HTTP post observable
    return this.http.post<VideoUploadResponse>(`${this.apiUrl}/videos/upload`, body);
  }

  // Additional methods remain the same
  getUserVideos(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/videos/user`);
  }

  getVideoStatus(videoId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/videos/${videoId}`);
  }
}