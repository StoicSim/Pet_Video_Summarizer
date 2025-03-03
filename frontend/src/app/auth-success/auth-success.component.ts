import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-auth-success',
  templateUrl: './auth-success.component.html',
  styleUrls: ['./auth-success.component.css']
})
export class AuthSuccessComponent implements OnInit {
  folderId: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.folderId = this.route.snapshot.queryParamMap.get('folder_id');

    // Auto-redirect to login after a few seconds
    setTimeout(() => {
      this.router.navigate(['/login']);
    }, 5000);
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }
}
