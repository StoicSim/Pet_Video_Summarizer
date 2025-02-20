import { Component, OnInit } from '@angular/core';
import { MatCalendarCellClassFunction } from '@angular/material/datepicker';

@Component({
  selector: 'app-date',
  templateUrl: './date.component.html',
  styleUrls: ['./date.component.css']
})
export class DateComponent implements OnInit {
  selectedDate: Date | null = null;
  hasSelectedDate: boolean = false;
  timelineEntry: any = null; // Will hold the entry data once date is selected

  constructor() { }

  ngOnInit(): void { }

  // Fix for the type error in the template
  dateClass: MatCalendarCellClassFunction<Date> = (cellDate, view) => {
    // Example implementation - customize as needed
    // This adds a custom class to dates that have entries
    // You would replace this logic with your actual data

    // For example, highlighting specific dates
    const hasEntry = this.hasEntryForDate(cellDate);
    return hasEntry ? 'date-with-entry' : '';
  }

  // Helper method to check if a date has an entry
  private hasEntryForDate(date: Date): boolean {
    // Replace with your actual logic to check if a date has entries
    // For example, comparing with dates from your backend
    return false; // Placeholder
  }

  onDateSelected(event: any) { // Changed from MatDatepickerInputEvent to any
    this.selectedDate = event;
    // Mock data - replace with actual API call
    this.timelineEntry = {
      petName: "Max",
      date: this.selectedDate,
      summary: "Max had a wonderful adventure at the park today! He made new friends and showed off his impressive fetch skills. His energy and enthusiasm brought joy to everyone around.",
      videoLink: "https://drive.google.com/file/d/example1",
      thumbnailUrl: "../../assets/max-thumbnail.jpg"
    };
    this.hasSelectedDate = true;
  }
}