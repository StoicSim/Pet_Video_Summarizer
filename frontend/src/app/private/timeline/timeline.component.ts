import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-timeline',
  templateUrl: './timeline.component.html',
  styleUrl: './timeline.component.css'
})
export class TimelineComponent implements OnInit {
  selectedFilter: 'today' | 'date' | 'week' | 'month' = 'today';
  userStreak: number = 0;
  hasContent: boolean = false;

  constructor(private route: Router, private path: ActivatedRoute) { }

  ngOnInit() {
    this.calculateStreak();
    const currentPath = this.path.snapshot.firstChild?.routeConfig?.path;
    if (currentPath === '') {
      this.selectedFilter = 'today';
    } else if (currentPath) {
      this.selectedFilter = currentPath as 'today' | 'date' | 'week' | 'month';
    }
    this.hasContent = true;
  }

  setFilter(filter: 'today' | 'date' | 'week' | 'month') {
    this.selectedFilter = filter;

    if (filter === 'today') {
      this.route.navigate(['./'], { relativeTo: this.path });
    } else {
      this.route.navigate([filter], { relativeTo: this.path });
    }

    this.hasContent = true;
  }

  private calculateStreak() {
    this.userStreak = 7;
  }
}