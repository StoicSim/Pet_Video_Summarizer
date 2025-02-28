import { importProvidersFrom, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatCardModule } from '@angular/material/card';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { HTTP_INTERCEPTORS } from '@angular/common/http';

import { AppComponent } from './app.component';
import { SharedComponent } from './shared/shared.component';
import { HomeComponent } from './shared/home/home.component';
import { PublicComponent } from './public/public.component';
import { PrivateComponent } from './private/private.component';
import { AboutComponent } from './public/about/about.component';
import { LoginComponent } from './public/login/login.component';
import { UserComponent } from './private/user/user.component';
import { TimelineComponent } from './private/timeline/timeline.component';
import { NavbarComponent } from './public/navbar/navbar.component';
import { RouterModule, Routes } from '@angular/router';
import { SignupComponent } from './public/signup/signup.component';
import { PrivateNavbarComponent } from './private/private-navbar/private-navbar.component';
import { TodayComponent } from './private/timeline/today/today.component';
import { DateComponent } from './private/timeline/date/date.component';
import { MonthComponent } from './private/timeline/month/month.component';
import { WeekComponent } from './private/timeline/week/week.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AuthGuard } from './auth.guard';
import { HttpClientModule } from '@angular/common/http';

import { AuthInterceptor } from './auth.interceptor';
import { VideoService } from './services/video.service';


const appRoutes: Routes = [
  {
    path: '',
    component: PublicComponent,
    children: [
      { path: '', component: HomeComponent },
      { path: 'about', component: AboutComponent },
      { path: 'login', component: LoginComponent },
      { path: 'signup', component: SignupComponent },
      {
        path: 'profile',
        component: UserComponent,
        canActivate: [AuthGuard]
      },
      {
        path: 'timeline',
        component: TimelineComponent,
        canActivate: [AuthGuard],
        children: [
          { path: '', component: TodayComponent },
          { path: 'date', component: DateComponent },
          { path: 'month', component: MonthComponent },
          { path: 'week', component: WeekComponent }
        ]
      }
    ]
  }
];



@NgModule({
  declarations: [
    AppComponent,
    SharedComponent,
    HomeComponent,
    PublicComponent,
    PrivateComponent,
    AboutComponent,
    LoginComponent,
    SignupComponent,
    UserComponent,
    TimelineComponent,
    NavbarComponent,
    PrivateNavbarComponent,
    DateComponent,
    MonthComponent,
    WeekComponent,

  ],
  imports: [
    FormsModule,
    ReactiveFormsModule,
    BrowserModule,
    RouterModule.forRoot(appRoutes),
    MatDatepickerModule,
    MatNativeDateModule,
    MatCardModule,
    BrowserAnimationsModule,

  ],
  providers: [
    provideAnimationsAsync(),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    importProvidersFrom(HttpClientModule),
    VideoService

  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
