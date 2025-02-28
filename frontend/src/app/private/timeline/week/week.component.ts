import { Component, OnInit } from '@angular/core';
import { VideoService, Video } from '../../../services/video.service';
import { AuthService } from '../../../services/auth.service';
import { Router } from '@angular/router';

interface FeatureCard {
  day: string;
  petName: string | null;
  summary: string;
  sourceVideoLink: string;
  summaryVideoLink: string;

  thumbnailUrl: string;
  actualVideo: Video | null;
}

@Component({
  selector: 'app-week',
  templateUrl: './week.component.html',
  styleUrls: ['./week.component.css']
})
export class WeekComponent implements OnInit {
  selectedDay: string | null = null;
  featureCards: FeatureCard[] = [];
  loading = true;
  error = '';

  // Fallback image if video thumbnail is not available
  defaultThumbnail = '../../assets/pic.png';

  // Days of the week in order
  daysOfWeek = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    'Friday', 'Saturday', 'Sunday'
  ];

  constructor(
    private videoService: VideoService,
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit(): void {
    // Check if user is logged in
    if (!this.authService.isLoggedIn()) {
      this.error = 'Please log in to view your weekly features';
      this.loading = false;
      return;
    }

    // Initialize with placeholder data
    this.initializePlaceholders();

    // Fetch featured videos
    this.loadFeaturedVideos();
  }

  private initializePlaceholders(): void {
    // Create placeholder cards for all days of the week
    this.featureCards = this.daysOfWeek.map(day => ({
      day,
      petName: null,
      summary: 'Loading...',
      sourceVideoLink: '',
      summaryVideoLink: '',
      thumbnailUrl: this.defaultThumbnail,
      actualVideo: null
    }));
  }

  loadFeaturedVideos(): void {
    this.videoService.getFeaturedVideos().subscribe({
      next: (featuredVideos) => {
        // Update feature cards with actual video data
        this.daysOfWeek.forEach(day => {
          const video = featuredVideos[day];
          const cardIndex = this.featureCards.findIndex(card => card.day === day);

          if (cardIndex !== -1) {
            if (video) {
              // Video exists for this day
              this.featureCards[cardIndex] = {
                day,
                petName: this.authService.getUserName() + "'s Pet",
                summary: video.summary_text || 'No summary available',
                sourceVideoLink: video.source_video_link,
                summaryVideoLink: video.summary_video_link,
                thumbnailUrl: this.generateThumbnailUrl(video),
                actualVideo: video
              };
            } else {
              // No video for this day
              this.featureCards[cardIndex] = {
                day,
                petName: null,
                summary: 'No videos available for this day yet. Upload a video to see it featured here!',
                sourceVideoLink: '',
                summaryVideoLink: '',
                thumbnailUrl: this.defaultThumbnail,
                actualVideo: null
              };
            }
          }
        });

        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading featured videos:', err);
        this.error = 'Failed to load your weekly features. Please try again later.';
        this.loading = false;
      }
    });
  }

  // Generate a thumbnail URL from the video
  private generateThumbnailUrl(video: Video): string {
    // If your backend generates thumbnails, use that URL
    if (video.summary_video_link) {
      // Try to create a thumbnail URL based on the video URL pattern
      // This is a simplified example - you may need to adjust based on your actual URL structure
      const videoUrl = video.summary_video_link;

      // If you're using YouTube videos
      if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
        const videoId = this.extractYouTubeId(videoUrl);
        if (videoId) {
          return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        }
      }

      // For other video services, you might need different methods
      // or return a frame capture from your backend
    }

    // Fallback to the default thumbnail
    return this.defaultThumbnail;
  }

  // Helper to extract YouTube video ID
  private extractYouTubeId(url: string): string | null {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  }

  selectDay(day: string): void {
    this.selectedDay = day;
  }

  getSelectedCard(): FeatureCard | undefined {
    return this.featureCards.find(card => card.day === this.selectedDay);
  }

  // Navigate to upload page if no video is available for the selected day
  uploadNewVideo(): void {
    this.router.navigate(['/upload']);
  }

  // Check if the currently selected card has a video
  hasVideo(): boolean {
    const card = this.getSelectedCard();
    return card ? !!card.actualVideo : false;
  }

  openVideo(): void {
    const card = this.getSelectedCard();
    if (card && card.summaryVideoLink) {
      window.open(card.summaryVideoLink, '_blank');
    }
  }
}