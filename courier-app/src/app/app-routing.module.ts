import { PackagesListComponent } from './packages-list/packages-list.component';
import { LabelsListComponent } from './labels-list/labels-list.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';


const routes: Routes = [
  {path: 'labels', component: LabelsListComponent},
  {path: 'packages', component: PackagesListComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
