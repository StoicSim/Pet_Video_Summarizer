import { Component, OnInit } from '@angular/core';

interface MemoryCard {
  title: string;
  date: Date;
  duration: string;
  summary: string;
  thumbnailUrl: string;
  videoLink: string;
}

@Component({
  selector: 'app-month',
  templateUrl: './month.component.html',
  styleUrls: ['./month.component.css']
})
export class MonthComponent implements OnInit {
  currentDate: Date = new Date();
  totalMemories: number = 0;
  monthMemories: MemoryCard[] = [
    {
      title: "Max's Beach Adventure",
      date: new Date(2024, 1, 15),
      duration: "2:30",
      summary: "Max had an incredible time at the beach today! He chased waves, built sandcastles, and made new furry friends.",
      thumbnailUrl: "../../assets/max-beach.jpg",
      videoLink: "https://example.com/video1"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    },
    {
      title: "Bella's Training Session",
      date: new Date(2024, 1, 18),
      duration: "3:45",
      summary: "Bella mastered new tricks during her training session. Her focus and dedication were impressive!",
      thumbnailUrl: "../../assets/bella-training.jpg",
      videoLink: "https://example.com/video2"
    }
    // Add more memory cards as needed
  ];

  constructor() {
    this.totalMemories = this.monthMemories.length;
  }

  ngOnInit(): void {
    // You can fetch the current month's memories here
  }
}