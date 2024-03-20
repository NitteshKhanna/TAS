import { Component, OnInit, OnDestroy } from '@angular/core';
import { log } from 'node:console';

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
  serverLink: string = "http://localhost:5000"
  signalCounterValues: number[] = [1, 2, 3, 4]
  timer: any;
  seconds: number = 0;
  signalDuration: number = 30;
  trafficLights: HTMLElement[] = [];
  pointer: number = 0;
  order: number[] = [1, 2, 3, 4];

  constructor() { }
  
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

  ngOnInit(): void
  {
    
    this.trafficLights = [
      (<HTMLElement>document.getElementById("tra1")),
      (<HTMLElement>document.getElementById("tra2")),
      (<HTMLElement>document.getElementById("tra3")),
      (<HTMLElement>document.getElementById("tra4"))
    ]

    document.querySelector(".start-cta")?.addEventListener("click", ()=>{
      (<HTMLElement>document.querySelector(".start-cta")).style.display = "none";
      this.startDetection();
      this.startFetchingCarCounts();
      this.setGreenLight(0);
      this.startTimer();
    (<HTMLElement>document.querySelector(".traffic-panel")).style.display = "flex";

    });
    (<HTMLElement>document.querySelector(".traffic-panel")).style.display = "none";
  }
  
  startFetchingCarCounts() {
    const feedCount = 4; 
    let carCounts: number[][] = [];
    for (let feedId = 1; feedId <= feedCount; feedId++) {
      
        fetch(`http://localhost:5000/car_count_feed_${feedId}`)
          .then(response => response.json())
          .then(data => {
            this.carCounts[feedId] = data.car_count;
            carCounts.push([feedId, data.car_count])
          })
          .catch(err => console.error(`Error fetching car count for feed ${feedId}:`, err));
    }
  }

  
  startTimer() {
    this.timer = setInterval(() => {
      this.signalCounterValues = this.signalCounterValues.map (time => {
        if(time == 0)
         {
          this.nextSignal();
          return 4 * this.signalDuration;
         }
         return time - 1;
      } );
    }, 1000);
  }

  setGreenLight(light: number) { 
    this.trafficLights.map(div => div.style.background = "linear-gradient(to right bottom, #d32628, red)");
    this.trafficLights[light].style.background = "linear-gradient(to right bottom, #0adb8b, green)";
  }

  nextSignal() {
    this.setGreenLight(this.order [(this.pointer == 3)? 0: ++this.pointer]);
  }
  ngOnDestroy() {
    clearInterval(this.timer);
  }
}
