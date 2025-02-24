import { Component, OnInit } from '@angular/core';

interface FeatureCard {
  day: string;
  petName: string;
  summary: string;
  videoLink: string;
  thumbnailUrl: string;
}

@Component({
  selector: 'app-week',
  templateUrl: './week.component.html',
  styleUrls: ['./week.component.css']
})
export class WeekComponent implements OnInit {
  selectedDay: string | null = null;
  featureCards: FeatureCard[] = [
    {
      day: 'Monday',
      petName: 'Max',
      summary: 'Max enjoyed a long walk at the beach, chasing seagulls and playing fetch with his favorite tennis ball. His boundless energy was on full display!',
      videoLink: 'https://drive.google.com/file/d/example-monday',
      thumbnailUrl: '../../assets/max-beach.jpg'
    },
    {
      day: 'Tuesday',
      petName: 'Bella',
      summary: 'Bella had her first training session and learned to sit and stay on command. She showed remarkable focus and intelligence throughout the session.',
      videoLink: 'https://drive.google.com/file/d/example-tuesday',
      thumbnailUrl: '../../assets/pic.png'
    },
    {
      day: 'Wednesday',
      petName: 'Charlie',
      summary: 'Charlie explored the new dog park in town, making friends with dogs of all sizes. He particularly enjoyed the agility course obstacles!',
      videoLink: 'https://drive.google.com/file/d/example-wednesday',
      thumbnailUrl: '../../assets/pic.png'
    },
    {
      day: 'Thursday',
      petName: 'Luna',
      summary: 'Luna had her spa day, getting a bath, haircut, and nail trim. She was pampered like royalty and looked absolutely gorgeous afterward.',
      videoLink: 'https://drive.google.com/file/d/example-thursday',
      thumbnailUrl: '../../assets/pic.png'
    },
    {
      day: 'Friday',
      petName: 'Cooper',
      summary: 'Cooper joined us for "Bring Your Pet to Work Day" and charmed everyone at the office. He was the perfect office assistant!',
      videoLink: 'https://drive.google.com/file/d/example-friday',
      thumbnailUrl: '../../assets/cooper-office.jpg'
    },
    {
      day: 'Saturday',
      petName: 'Lucy',
      summary: 'Lucy went hiking with her family and conquered a 5-mile trail. Her excitement at reaching the summit viewpoint was contagious!',
      videoLink: 'https://drive.google.com/file/d/example-saturday',
      thumbnailUrl: '../../assets/lucy-hiking.jpg'
    },
    {
      day: 'Sunday',
      petName: 'Oliver',
      summary: 'Oliver enjoyed a lazy Sunday at home, cuddling on the couch and watching movies with his family. Perfect end to a busy week!',
      videoLink: 'https://drive.google.com/file/d/example-sunday',
      thumbnailUrl: '../../assets/oliver-relaxing.jpg'
    }
  ];

  constructor() { }

  ngOnInit(): void {
  }

  selectDay(day: string): void {
    this.selectedDay = day;
  }

  getSelectedCard(): FeatureCard | undefined {
    return this.featureCards.find(card => card.day === this.selectedDay);
  }
}