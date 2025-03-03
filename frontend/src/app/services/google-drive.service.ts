import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { switchMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class GoogleDriveService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  // Get Google OAuth authorization URL
  getAuthUrl(): Observable<any> {
    return this.authService.getCurrentUser().pipe(
      switchMap(user => {
        const userId = user?.id;
        return this.http.get(`${this.apiUrl}/google/auth?user_id=${userId}`);
      })
    );
  }

  // Upload a file to Google Drive folder
  uploadFileToDrive(filePath: string): Observable<any> {
    return this.authService.getCurrentUser().pipe(
      switchMap(user => {
        const userId = user?.id;
        return this.http.post(`${this.apiUrl}/upload-to-drive`, {
          file_path: filePath,
          user_id: userId
        });
      })
    );
  }
}
