import { Component, OnInit } from '@angular/core';
import { VideoService, Video } from '../../../services/video.service';
import { AuthService } from '../../../services/auth.service';
import { CommonModule } from '@angular/common';

interface TimelineEntry {
  petName: string;
  summary: string;
  videoLink: string;
  thumbnailUrl: string;
  animalType: string;
  processingStatus: string;
  sourceVideoLink: string;
}

@Component({
  selector: 'app-today',
  templateUrl: './today.component.html',
  styleUrls: ['./today.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class TodayComponent implements OnInit {
  entry: TimelineEntry = {
    petName: '',
    summary: '',
    videoLink: '',
    thumbnailUrl: '../../assets/pic.png',
    animalType: '',
    processingStatus: '',
    sourceVideoLink: ''
  };

  loading: boolean = true;
  hasVideoToday: boolean = false;
  error: string | null = null;

  constructor(
    private videoService: VideoService,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    this.fetchTodayVideo();
  }

  fetchTodayVideo(): void {
    if (!this.authService.isLoggedIn()) {
      this.loading = false;
      this.error = 'Please log in to view your daily pet summary';
      return;
    }

    this.videoService.getTodayVideo().subscribe({
      next: (video) => {
        this.loading = false;

        if (video) {
          this.hasVideoToday = true;

          // Get pet name from user data
          const userData = JSON.parse(localStorage.getItem('userData') || '{}');
          // For now, we'll use the animal type as the pet name if user's pet name isn't available
          const petName = userData.petName || video.animal_type || 'Pet';

          // Customize summary message based on processing status
          let summaryText = '';
          if (video.processing_status === 'completed') {
            summaryText = video.summary_text || 'No summary available yet.';
          } else {
            summaryText = `Your video is currently being processed (${video.processing_status}).`;
          }

          this.entry = {
            petName: petName,
            summary: summaryText,
            videoLink: video.processing_status === 'completed' ? (video.summary_video_link || '') : '',
            thumbnailUrl: '../../assets/pic.png',
            animalType: video.animal_type || 'pet',
            processingStatus: video.processing_status,
            sourceVideoLink: video.source_video_link || ''
          };
        } else {
          this.hasVideoToday = false;
          this.entry = {
            petName: 'Your Pet',
            summary: 'You haven\'t uploaded any videos of your pet today.',
            videoLink: '',
            thumbnailUrl: '../../../../assets/pic.png',
            animalType: '',
            processingStatus: '',
            sourceVideoLink: ''
          };
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Failed to load today\'s video. Please try again later.';
        console.error('Error fetching today\'s video:', err);
      }
    });
  }
  openSummaryVideo() {
    if (this.entry.videoLink && this.entry.processingStatus === 'completed') {
      window.open(this.entry.videoLink, '_blank');
    }
  }
}