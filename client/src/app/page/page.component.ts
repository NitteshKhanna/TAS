import { Component, OnInit, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-page',
  standalone: true,
  imports: [],
  templateUrl: './page.component.html',
  styleUrl: './page.component.scss'
})
export class PageComponent {
  carCounts: { [feedId: number]: number } = {};
  private intervalIds: any[] = [];

  constructor() { }
  serverLink: string = "http://127.0.0.1:5000"
  startDetection(): void {
    fetch(this.serverLink + '/start_all_feeds', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  stopDetection(): void {
    fetch(this.serverLink + '/stop_detection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  restartDetection(): void {
    fetch(this.serverLink + '/restart_detection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  ngOnInit(): void
  {
    
    document.querySelector(".start-cta")?.addEventListener("click", ()=>{
      (<HTMLElement>document.querySelector(".start-cta")).style.display = "none";
      this.startDetection();
      this.startFetchingCarCounts();
    (<HTMLElement>document.querySelector(".ctn")).style.display = "flex";

    });
    (<HTMLElement>document.querySelector(".ctn")).style.display = "none";
  }
  ngOnDestroy() {
    this.intervalIds.forEach(clearInterval);
    
  }
  startFetchingCarCounts() {
    const feedCount = 4; // Assuming there are 4 feeds
    for (let feedId = 1; feedId <= feedCount; feedId++) {
      const intervalId = setInterval(() => {
        fetch(`http://localhost:5000/car_count_feed_${feedId}`)
          .then(response => response.json())
          .then(data => {
            this.carCounts[feedId] = data.car_count;
          })
          .catch(err => console.error(`Error fetching car count for feed ${feedId}:`, err));
      }, 3000); // Update car count every 3 seconds
      this.intervalIds.push(intervalId);
    }
  }
}
