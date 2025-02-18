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

@NgModule({
  declarations: [
    AppComponent,
    SharedComponent,
    HomeComponent,
    PublicComponent,
    PrivateComponent,
    AboutComponent,
    LoginComponent,
    UserComponent,
    TimelineComponent,
    NavbarComponent
  ],
  imports: [
    BrowserModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
