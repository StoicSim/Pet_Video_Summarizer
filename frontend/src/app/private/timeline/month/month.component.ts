import { Component, OnInit } from '@angular/core';
import { VideoService, Video, Memory } from '../../../services/video.service';

@Component({
  selector: 'app-month',
  templateUrl: './month.component.html',
  styleUrls: ['./month.component.css']
})
export class MonthComponent implements OnInit {
  currentDate = new Date();
  totalMemories = 0;
  monthMemories: Memory[] = [];
  isLoading = true;
  errorMessage = '';

  constructor(private videoService: VideoService) { }

  ngOnInit(): void {
    this.loadMonthVideos();
  }

  loadMonthVideos(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.videoService.getCurrentMonthVideos().subscribe({
      next: (videos) => {
        this.totalMemories = videos.length;
        // Convert backend Video objects to frontend Memory objects
        this.monthMemories = this.videoService.convertToMemories(videos);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading month videos:', error);
        this.errorMessage = 'Failed to load memories. Please try again later.';
        this.isLoading = false;
      }
    });
  }

  // Method to handle video click
  watchVideo(videoLink: string): void {
    // You could either navigate to a dedicated video player page
    // or open the video in a modal/lightbox
    window.open(videoLink, '_blank');
  }
}