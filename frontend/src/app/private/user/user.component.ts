import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent implements OnInit {
  basicInfoForm: FormGroup;
  passwordForm: FormGroup;
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(private fb: FormBuilder) {
    this.basicInfoForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      dogName: ['', Validators.required]
    });

    this.passwordForm = this.fb.group({
      currentPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    }, { validator: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Load user data
    this.loadUserData();
  }

  loadUserData(): void {
    // Fetch user data and populate the form
    const userData = {
      email: 'user@example.com',
      dogName: 'Max'
    };
    this.basicInfoForm.patchValue(userData);
  }

  passwordMatchValidator(g: FormGroup) {
    return g.get('newPassword')?.value === g.get('confirmPassword')?.value
      ? null : { 'mismatch': true };
  }

  updateBasicInfo(): void {
    if (this.basicInfoForm.valid) {
      console.log('Updating basic info:', this.basicInfoForm.value);
      // Handle the form submission here
      alert('Basic info updated successfully!');
      this.basicInfoForm.markAsPristine();
    }
  }

  updatePassword(): void {
    if (this.passwordForm.valid) {
      console.log('Updating password:', this.passwordForm.value);
      // Handle the password update here
      alert('Password updated successfully!');
      this.passwordForm.reset();
      this.showCurrentPassword = false;
      this.showNewPassword = false;
      this.showConfirmPassword = false;
    }
  }
}