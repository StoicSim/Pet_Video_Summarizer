import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

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

const appRoutes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },

  { path: 'private', component: PrivateComponent }


]
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
    NavbarComponent
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot(appRoutes)
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
