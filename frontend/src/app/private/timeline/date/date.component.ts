import { Component, OnInit } from '@angular/core';
import { MatCalendarCellClassFunction } from '@angular/material/datepicker';
import { VideoService, Video } from '../../../services/video.service';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-date',
  templateUrl: './date.component.html',
  styleUrls: ['./date.component.css']
})
export class DateComponent implements OnInit {
  selectedDate: Date | null = null;
  hasSelectedDate: boolean = false;
  timelineEntry: Video | null = null;
  loading: boolean = false;
  error: string | null = null;

  constructor(private videoService: VideoService) { }

  ngOnInit(): void { }

  dateClass: MatCalendarCellClassFunction<Date> = (cellDate, view) => {
    // This logic should be implemented based on your backend data
    // For now, we'll return an empty string
    return '';
  }

  onDateSelected(event: Date) {
    this.selectedDate = event;
    this.hasSelectedDate = true;
    this.loading = true;
    this.error = null;

    // Create a new date object and set it to midnight in the local timezone
    // This prevents timezone issues when converting to ISO string
    const localDate = new Date(event);

    console.log("Selected date in calendar:", event);
    console.log("Date being used for API call:", localDate);

    this.videoService.getVideosByDate(localDate).pipe(
      catchError(err => {
        console.error("Error fetching videos:", err);
        this.error = 'An error occurred while fetching the video data.';
        return of([]);
      })
    ).subscribe(videos => {
      this.loading = false;
      console.log(`Received ${videos.length} videos for date:`, localDate);
      if (videos.length > 0) {
        this.timelineEntry = videos[0]; // Assuming we show the first video for the day
      } else {
        this.timelineEntry = null;
        this.error = 'No videos found for this date.';
      }
    });
  }
}
