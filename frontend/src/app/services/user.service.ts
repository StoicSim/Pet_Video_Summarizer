import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  registerUser(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData).pipe(
      tap(response => {
        // After successful registration, redirect to Google OAuth page
        if (response && response.user_id) {
          this.router.navigate(['/google-auth'], {
            queryParams: { user_id: response.user_id }
          });
        }
      })
    );
  }
}