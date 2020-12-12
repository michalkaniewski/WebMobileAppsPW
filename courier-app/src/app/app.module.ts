import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LabelsListComponent } from './labels-list/labels-list.component';
import { PackagesListComponent } from './packages-list/packages-list.component';

@NgModule({
  declarations: [
    AppComponent,
    LabelsListComponent,
    PackagesListComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
