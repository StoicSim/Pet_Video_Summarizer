import { Component, OnInit } from '@angular/core';

interface TimelineEntry {
  petName: string;
  summary: string;
  videoLink: string;
  thumbnailUrl: string;
}

@Component({
  selector: 'app-today',
  templateUrl: './today.component.html',
  styleUrls: ['./today.component.css']
})
export class TodayComponent implements OnInit {
  entry: TimelineEntry =
    {
      petName: 'Max',
      summary: 'Max had a wonderful adventure at the park today! He made new friends and showed off his impressive fetch skills. His energy and enthusiasm brought joy to everyone around.',
      videoLink: 'https://drive.google.com/file/d/example1',
      thumbnailUrl: '../../assets/max-thumbnail.jpg'
    };
  // Add more entries as needed


  constructor() { }

  ngOnInit(): void {
    // Initialize any necessary data
  }
}