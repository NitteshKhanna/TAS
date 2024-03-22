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
  carCounts: { [feedId: number]: number } = {1: 0, 2: 0, 3: 0, 4: 0};
  private intervalIds: any[] = [];
  serverLink: string = "http://localhost:5000"
  signalCounterValues: number[] = [0, 15, 30, 60]
  timer: any;
  seconds: number = 0;
  signalDuration: number = 30;
  trafficLights: HTMLElement[] = [];
  pointer: number = 0;
  order: number[] = [1, 2, 3, 4];
  congestions: HTMLElement[] = [];
  hasTimerStarted: boolean = false;
  images: HTMLElement[] = [];

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
      this.startFetchingCarCounts();
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  ngOnInit(): void
  {
    this.congestions = [
      (<HTMLElement>document.getElementById("congestion1")),
      (<HTMLElement>document.getElementById("congestion3")),
      (<HTMLElement>document.getElementById("congestion4")),
      (<HTMLElement>document.getElementById("congestion2"))
    ];
    
    this.trafficLights = [
      (<HTMLElement>document.getElementById("tra1")),
      (<HTMLElement>document.getElementById("tra3")),
      (<HTMLElement>document.getElementById("tra4")),
      (<HTMLElement>document.getElementById("tra2"))
    ]
    
    this.images = [
      (<HTMLElement>document.getElementById("img1")),
      (<HTMLElement>document.getElementById("img3")),
      (<HTMLElement>document.getElementById("img4")),
      (<HTMLElement>document.getElementById("img2"))
    ]

    document.querySelector(".start-cta")?.addEventListener("click", ()=>{
      (<HTMLElement>document.querySelector(".start-cta")).style.display = "none";
      this.startDetection();
      
    (<HTMLElement>document.querySelector(".traffic-panel")).style.display = "flex";

    });
    (<HTMLElement>document.querySelector(".traffic-panel")).style.display = "none";
  }
  
  startFetchingCarCounts() {
    const feedCount = 4; 
    let carCounts: number[][] = [], sortedCarCounts: number[][] = [], i, j, min, t, len;
    
    for (let feedId = 1; feedId <= feedCount; feedId++) {
        setInterval(() => {
        
          fetch(`http://localhost:5000/car_count_feed_${feedId}`)
            .then(response => response.json())
            .then(data => {
              this.carCounts[feedId] = data.car_count;
              console.log(feedId, data.car_count);
              let congestiontxt = this.congestions[feedId - 1];
              
              if(data.car_count < 5)
              {
                congestiontxt.style.color = "green"; 
                congestiontxt.textContent = "LOW";
                this.images[feedId - 1].style.border = "#57d28b .2rem solid"
              }
              else if(data.car_count >= 5 && data.car_count < 10)
              {
                congestiontxt.style.color = "orange"; 
                congestiontxt.textContent = "MEDIUM";
                this.images[feedId - 1].style.border = "orange .2rem solid"
              }
              else
              {
                congestiontxt.style.color = "red"; 
                congestiontxt.textContent = "HIGH";
                this.images[feedId - 1].style.border = "red .2rem solid"
              }
              if(!this.hasTimerStarted)
                {
                  this.startTimer();
                  this.hasTimerStarted = true;
                }
            })
            .catch(err => console.error(`Error fetching car count for feed ${feedId}:`, err));
          }, 1000)
      }
    
    function createSignalValues(signalDuration: number)
    {

      // for (i = 0, len = carCounts.length; i < len; i++)
      // {
      //   min = carCounts[i];
        
      //   for (j = i; j < len; j++)
      //   {
      //     if (min[1] > carCounts[j][1])
      //     {
      //       t = min[1];
      //       min[1] = carCounts[j][1];
      //       carCounts[j][1] = t;
      //     }
      //   }
      //   sortedCarCounts.push(min);
      // }
  
      // let signalCounterValues = [];
      
      // for (i = 0; i < len; i++)
      // {
      //   for (j = 0; j < len; j++)
      //   {
      //     if (sortedCarCounts[j][0] == i)
      //     {
      //       signalCounterValues.push(((i + 1) * signalDuration))
      //     }
      //   }
      // }
      
      
      // return signalCounterValues;
    }
  }

  
  startTimer() {
    this.timer = setInterval(() => {
      this.signalCounterValues = this.signalCounterValues.map (time => {
        if(time == 0)
         {
          console.log("switching");
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
    console.log(this.pointer);
    if(this.pointer == 3)
      this.pointer = 0;
    else
      this.pointer++;

    this.setGreenLight(this.order [this.pointer] - 1 );
  }
  ngOnDestroy() {
    clearInterval(this.timer);
  }
}
