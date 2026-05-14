<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Tvätteri Routeplanner – Standalone</title>
  <style>
    :root{--bg:#f8fafc;--card:#fff;--border:#e2e8f0;--text:#0f172a;--muted:#475569;--primary:#0f172a;--danger:#b91c1c;--ok:#166534;}
    *{box-sizing:border-box}
    body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--text)}
    header{position:sticky;top:0;background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border)}
    .wrap{max-width:1500px;margin:0 auto;padding:14px 16px}
    .row{display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
    h1{font-size:16px;margin:0}
    .btn{border:1px solid var(--border);background:#fff;color:var(--text);padding:10px 12px;border-radius:12px;font-weight:800;font-size:13px;cursor:pointer}
    .btn.primary{background:var(--primary);color:#fff;border-color:var(--primary)}
    .btn.danger{color:var(--danger)}
    .grid{display:grid;grid-template-columns:260px 1fr;gap:14px;align-items:start}
    @media (max-width:900px){.grid{grid-template-columns:1fr}}
    .card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:14px;box-shadow:0 1px 1px rgba(0,0,0,.02)}
    .card h2{margin:0 0 6px;font-size:14px}
    .sub{color:var(--muted);font-size:12px;margin:0 0 10px}
    label{font-size:12px;font-weight:800;display:block;margin-bottom:6px}
    input,select{width:100%;padding:10px;border:1px solid var(--border);border-radius:12px;font-size:13px;background:#fff}
    .field{display:grid;gap:6px}
    .cols2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
    .cols3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
    @media (max-width:700px){.cols2,.cols3{grid-template-columns:1fr}}
    .chip{display:inline-flex;align-items:center;gap:6px;background:#f1f5f9;border:1px solid var(--border);padding:4px 8px;border-radius:999px;font-size:12px;color:var(--muted)}
    .list{display:grid;gap:10px}
    .item{border:1px solid var(--border);border-radius:16px;padding:12px;background:#fff}
    .itemhead{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .itemtitle{font-weight:900}
    .small{font-size:12px;color:var(--muted)}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th,td{padding:8px 10px;border-top:1px solid var(--border);text-align:left;vertical-align:top}
    thead th{background:#f8fafc;border-top:none;color:var(--muted);font-size:12px}
    .notice{border:1px solid var(--border);border-radius:14px;padding:10px;font-size:13px}
    .notice.ok{border-color:#bbf7d0;background:#f0fdf4;color:var(--ok)}
    .notice.bad{border-color:#fecaca;background:#fef2f2;color:var(--danger)}
    .tabs{display:flex;gap:8px;flex-wrap:wrap}
    .tab{padding:10px 12px;border-radius:12px;border:1px solid var(--border);background:#fff;font-weight:900;font-size:13px;cursor:pointer}
    .tab.active{background:var(--primary);color:#fff;border-color:var(--primary)}
  
    /* --- UX improvements --- */

    .numIcon{
      background:var(--primary);
      color:#fff;
      width:28px;height:28px;
      border-radius:999px;
      display:flex;align-items:center;justify-content:center;
      font-weight:900;
      border:2px solid #fff;
      box-shadow:0 2px 6px rgba(0,0,0,.18);
      font-size:12px;
    }


    .planGrid{display:grid;grid-template-columns:minmax(420px,1fr) minmax(560px,1.35fr);gap:14px;align-items:start}
    @media (max-width:900px){.planGrid{grid-template-columns:1fr}}
    .mapCard{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:14px;box-shadow:0 1px 1px rgba(0,0,0,.02)}

    .sectionCard{border-radius:20px}
    .section-depot{background:linear-gradient(180deg,#ffffff 0%, #f8fafc 100%)}
    .section-vehicles{background:linear-gradient(180deg,#ffffff 0%, #f6fffb 100%)}
    .section-customers{background:linear-gradient(180deg,#ffffff 0%, #f8f7ff 100%)}
    .card + .card{margin-top:12px}
    input:focus, select:focus{outline:3px solid rgba(15,23,42,.20); border-color:rgba(15,23,42,.35)}
    .focusHint{box-shadow:0 0 0 3px rgba(15,23,42,.15)}
    .link{color:var(--primary); text-decoration:underline; cursor:pointer; font-weight:900}

  </style>

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>

</head>
<body>
<header>
  <div class="wrap">
    <div class="row">
      <div style="display:flex;align-items:center;gap:10px">
        <h1>Tvätteri Routeplanner</h1>
        <span class="chip">Standalone (ingen internet / npm)</span>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <button class="btn primary" id="btnGenerate">Generera rutter</button>
        <button class="btn" id="btnExport">Export JSON</button>

        <button class="btn" id="btnExportCsv">Export rutter (CSV)</button>
        <label class="btn" style="display:inline-flex;align-items:center;gap:8px;cursor:pointer">
          Import kunder (CSV) <input type="file" id="importCustomersCsv" accept=".csv,text/csv" style="display:none"/>
        </label>
        <label class="btn" style="display:inline-flex;align-items:center;gap:8px;cursor:pointer">
          Import fordon (CSV) <input type="file" id="importVehiclesCsv" accept=".csv,text/csv" style="display:none"/>
        </label>
        <button class="btn" id="btnDownloadTemplates">CSV-mallar</button>

        <label class="btn" style="display:inline-flex;align-items:center;gap:8px;cursor:pointer">
          Import JSON <input type="file" id="importFile" accept="application/json" style="display:none"/>
        </label>
        <button class="btn danger" id="btnReset">Återställ demo</button>
      </div>
    </div>
  </div>
</header>

<main class="wrap">
  <div class="grid">
    <aside class="card">
      <h2>Navigation</h2>
      <p class="sub">Fyll data → generera → se resultat</p>
      <div class="tabs">
        <button class="tab active" id="tabData">Data</button>
        <button class="tab" id="tabPlan">Planering</button>
      </div>
      <div style="height:10px"></div>
      <div class="notice" id="statusBox">Ingen plan ännu.</div>
      <div style="height:10px"></div>
      <p class="sub"><b>Tips:</b> Ange lat/lon för depå och kunder för distans/tid.</p>
      <p class="small">OBS: Offline – ingen OSM-geokodning här.</p>
    </aside>

    <section id="viewData" class="card">
      <h2>Data</h2>
      <p class="sub">Depå, fordon, kunder</p>

      <div class="card" style="padding:12px;margin-bottom:12px">
        <div class="cols2">
          <div class="field">
            <label>Depå adress</label>
            <input id="depotAddress" placeholder="t.ex. Göteborg"/>
          </div>
          <div class="cols2">
            <div class="field"><label>Depå lat</label><input id="depotLat" type="number" step="any"/></div>
            <div class="field"><label>Depå lon</label><input id="depotLon" type="number" step="any"/></div>
          </div>
        </div>
        <div style="height:10px"></div>
        <button class="btn" id="btnGeocodeDepot">Hämta koordinater från adress</button>
      </div>

      <div class="card" style="padding:12px;margin-bottom:12px">
        <div class="row">
          <div>
            <div class="itemtitle">Fordon</div>
            <div class="small">Varje fordon kan skapa 1 rutt per dag (MVP)</div>
          </div>
          <button class="btn primary" id="addVehicle">+ Lägg till</button>
        </div>
        <div style="height:10px"></div>
        <div id="vehiclesList" class="list"></div>
      </div>

      <div class="card" style="padding:12px">
        <div class="row">
          <div>
            <div class="itemtitle">Kunder</div>
            <div class="small">Leveranser/vecka + tillåtna dagar + containers</div>
          </div>
          <button class="btn primary" id="addCustomer">+ Lägg till</button>
        </div>
        <div style="height:10px"></div>
        <div id="customersList" class="list"></div>
      </div>
    </section>

    <section id="viewPlan" class="card" style="display:none">
      <h2>Planering</h2>
      <p class="sub">Rutter per dag och fordon</p>
            <div class="planGrid">
        <div>
          <div id="planSummary" class="cols3" style="margin-bottom:12px"></div>
          <div id="planIssues" style="margin-bottom:12px"></div>
          <div id="planRoutes" class="list"></div>
        </div>
        <div class="mapCard">
          <div class="row" style="margin-bottom:8px">
            <div>
              <div style="font-weight:900">Karta</div>
              <div class="small">Visar depå, kunder och vald rutt. Klicka en rutt för att visa linje.</div>
            </div>
            <button class="btn" id="btnFitMap">Fokusera</button>
          </div>
          <div id="map" style="height:760px;border:1px solid var(--border);border-radius:16px"></div>
          <div class="small" style="margin-top:8px;color:var(--muted)">Obs: Kartan kräver internet (OpenStreetMap tiles).</div>
        </div>
      </div>
    </section>
  </div>
</main>

<script>
  const STORAGE_KEY = "laundry_routeplanner_standalone_v1";
  const DAYS = ["Mon","Tue","Wed","Thu","Fri"];
  const uid = () => Math.random().toString(16).slice(2) + Date.now().toString(16);
  const safeNum = (x,f=0) => Number.isFinite(Number(x)) ? Number(x) : f;
  const clamp = (n,min,max) => Math.max(min, Math.min(max, n));
  const deepCopy = (x) => JSON.parse(JSON.stringify(x));

  function escapeHtml(str){
    return String(str??"").replace(/[&<>"']/g, s=>({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[s]));
  }


  async function geocodeAddress(query){
    const q = String(query||"").trim();
    if(!q) return null;
    const url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + encodeURIComponent(q);
    const res = await fetch(url, {headers: {"Accept":"application/json"}});
    if(!res.ok) return null;
    const data = await res.json();
    if(!Array.isArray(data) || !data.length) return null;
    return {lat: Number(data[0].lat), lon: Number(data[0].lon), displayName: data[0].display_name};
  }

  async function geocodeDepot(){
    const q = state.depot.address || "";
    const hit = await geocodeAddress(q);
    if(!hit || !Number.isFinite(hit.lat) || !Number.isFinite(hit.lon)){
      alert("Kunde inte hitta koordinater för depån. Kontrollera adressen.");
      return;
    }
    state.depot.lat = hit.lat;
    state.depot.lon = hit.lon;
    save(); render();
    setView("plan");
    renderMapStatic();
  }

  async function geocodeCustomer(customerId){
    const c = (state.customers||[]).find(x=>x.id===customerId);
    if(!c){ return; }
    const q = (c.address && String(c.address).trim()) ? c.address : c.name;
    const hit = await geocodeAddress(q);
    if(!hit || !Number.isFinite(hit.lat) || !Number.isFinite(hit.lon)){
      alert(`Kunde inte hitta koordinater för "${c.name}". Kontrollera adressen.`);
      return;
    }
    c.lat = hit.lat;
    c.lon = hit.lon;
    save(); render();
    setView("plan");
    renderMapStatic();
  }

  function demoProject(){
    return {
      id: uid(),
      depot: { address:"Göteborg", lat:57.7089, lon:11.9746 },
      vehicles: [
        { id:"CAR-1", name:"Lastbil 1", capacityContainers:70, trailerAttached:false, trailerCapacityContainers:0, meanSpeedKmh:40, maxDriveMinutesPerDay:480, weeklyTrips:4, priority:1 },
        { id:"CAR-2", name:"Lastbil 2 med släp", capacityContainers:50, trailerAttached:true, trailerCapacityContainers:30, meanSpeedKmh:38, maxDriveMinutesPerDay:480, weeklyTrips:4, priority:2 },
      ],
      customers: [
        { id:"CUST-1", name:"Hotell A", address:"Centrum", lat:57.708, lon:11.974, containersPerDelivery:18, deliveriesPerWeek:2, allowedDays:["Mon","Thu","Fri"], minWeekdaysBetween:1, timeWindowStart:"09:00", timeWindowEnd:"12:00", serviceMinutes:20, vehicleAllowedIds:[] },
        { id:"CUST-2", name:"Restaurang B", address:"Hisingen", lat:57.72, lon:11.93, containersPerDelivery:10, deliveriesPerWeek:1, allowedDays:["Tue","Wed","Thu"], minWeekdaysBetween:0, timeWindowStart:"13:00", timeWindowEnd:"16:00", serviceMinutes:15, vehicleAllowedIds:["CAR-2"] },
        { id:"CUST-3", name:"Gym C", address:"Mölndal", lat:57.66, lon:12.02, containersPerDelivery:22, deliveriesPerWeek:3, allowedDays:["Mon","Wed","Fri"], minWeekdaysBetween:1, timeWindowStart:"08:00", timeWindowEnd:"11:00", serviceMinutes:25, vehicleAllowedIds:[] },
      ],
      settings:{ allowOverCap:0, startTime:"07:00", timeWindowPriority:true },
      lastRoutes:null
    };
  }

  let state;

  function load(){
    const raw = localStorage.getItem(STORAGE_KEY);
    if(raw){
      try { state = JSON.parse(raw); }
      catch { state = demoProject(); }
    } else state = demoProject();
  }
  function save(){ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }

  function minutesFromHHMM(hhmm){
    if(!hhmm) return null;
    const [h,m] = hhmm.split(":").map(x=>parseInt(x,10));
    if(Number.isNaN(h)||Number.isNaN(m)) return null;
    return h*60+m;
  }
  function hhmmFromMinutes(mins){
    if(mins==null) return "";
    const h=Math.floor(mins/60), m=mins%60;
    return String(h).padStart(2,"0")+":"+String(m).padStart(2,"0");
  }
  function haversineKm(a,b){
    const R=6371;
    const dLat=(b.lat-a.lat)*Math.PI/180;
    const dLon=(b.lon-a.lon)*Math.PI/180;
    const lat1=a.lat*Math.PI/180, lat2=b.lat*Math.PI/180;
    const sinDLat=Math.sin(dLat/2), sinDLon=Math.sin(dLon/2);
    const aa=sinDLat*sinDLat + Math.cos(lat1)*Math.cos(lat2)*sinDLon*sinDLon;
    const c=2*Math.atan2(Math.sqrt(aa),Math.sqrt(1-aa));
    return R*c;
  }
  function validateCoords(label,obj){
    const lat=Number(obj.lat), lon=Number(obj.lon);
    if(!Number.isFinite(lat)||!Number.isFinite(lon)) return label+": koordinater saknas/ogiltiga";
    if(lat<-90||lat>90||lon<-180||lon>180) return label+": koordinater utanför intervall";
    return null;
  }
  function estimateTravelMinutes(km,speed){ return Math.round((km/Math.max(5,speed))*60); }
  function vehicleTotalCapacity(vehicle){
    return safeNum(vehicle?.capacityContainers,0) + (vehicle?.trailerAttached ? safeNum(vehicle?.trailerCapacityContainers,0) : 0);
  }
  function buildDistanceMatrix(nodes){
    const map=new Map(nodes.map(n=>[n.id,n]));
    const ids=nodes.map(n=>n.id);
    const dist={};
    for(const i of ids){
      dist[i]={};
      for(const j of ids){
        if(i===j) dist[i][j]=0;
        else{
          const a=map.get(i), b=map.get(j);
          dist[i][j]=haversineKm({lat:a.lat,lon:a.lon},{lat:b.lat,lon:b.lon});
        }
      }
    }
    return dist;
  }
  function customerTightnessScore(c){
    const hasTW=c.timeWindowStart && c.timeWindowEnd;
    const twWidth = hasTW ? clamp(minutesFromHHMM(c.timeWindowEnd)-minutesFromHHMM(c.timeWindowStart),0,1440) : 1440;
    const twScore = hasTW ? (1440-twWidth)/60 : 0;
    const vehicleScore = (c.vehicleAllowedIds && c.vehicleAllowedIds.length) ? 10 : 0;
    const serviceScore = safeNum(c.serviceMinutes,0)/10;
    const volScore = safeNum(c.containers,0)/5;
    const allowedDaysScore = c.allowedDays && c.allowedDays.length ? (7 - c.allowedDays.length) : 0;
    return twScore + vehicleScore + serviceScore + volScore + allowedDaysScore;
  }
  function weekdayIndex(day){ return DAYS.indexOf(day); }
  function weekdaysBetween(aDay,bDay){
    const a=weekdayIndex(aDay), b=weekdayIndex(bDay);
    if(a<0||b<0) return 0;
    const diff=Math.abs(b-a);
    return Math.max(0,diff-1);
  }
  function canPlaceDelivery(day, chosen, minGap){
    const g=safeNum(minGap,0);
    if(!g) return true;
    for(const d of chosen) if(weekdaysBetween(day,d) < g) return false;
    return true;
  }
  function averageCoordForAssignments(assignments, customerById){
    const pts=(assignments||[])
      .map(a=>customerById.get(a.customerId))
      .filter(c=>c && Number.isFinite(c.lat) && Number.isFinite(c.lon));
    if(!pts.length) return null;
    const sum=pts.reduce((acc,c)=>({lat:acc.lat+c.lat, lon:acc.lon+c.lon}), {lat:0,lon:0});
    return {lat:sum.lat/pts.length, lon:sum.lon/pts.length};
  }
  function combinations(arr,k){
    const out=[];
    function rec(start,cur){
      if(cur.length===k){ out.push([...cur]); return; }
      for(let i=start;i<=arr.length-(k-cur.length);i++){
        cur.push(arr[i]); rec(i+1,cur); cur.pop();
      }
    }
    if(k<0 || k>arr.length) return out;
    rec(0,[]);
    return out;
  }

  function planRoutes(project){
    const p=deepCopy(project);
    const issues=[];
    const depotIssue=validateCoords("Depå", p.depot);
    if(depotIssue) issues.push({type:"DATA", message:depotIssue});
    if(!p.vehicles.length) issues.push({type:"DATA", message:"Inga fordon – lägg till minst 1"});
    if(!p.customers.length) issues.push({type:"DATA", message:"Inga kunder – lägg till minst 1"});

    // Normalize vehicles + weekly trips
    const vehicles=[...p.vehicles].map(v=>({
      ...v,
      id: String(v.id||"").trim() || ("CAR-"+uid().slice(0,4)),
      name: (v.name!=null && String(v.name).trim()) ? String(v.name).trim() : String(v.id||"Bil"),
      capacityContainers:safeNum(v.capacityContainers,0),
      trailerAttached:Boolean(v.trailerAttached),
      trailerCapacityContainers:clamp(safeNum(v.trailerCapacityContainers,0),0,100000),
      meanSpeedKmh:clamp(safeNum(v.meanSpeedKmh,40),5,130),
      maxDriveMinutesPerDay:clamp(safeNum(v.maxDriveMinutesPerDay,480),30,1440),
      weeklyTrips:clamp(safeNum(v.weeklyTrips,5),1,7),
      priority:safeNum(v.priority,0),
    })).sort((a,b)=>a.priority!==b.priority ? a.priority-b.priority : vehicleTotalCapacity(b)-vehicleTotalCapacity(a));

    // Track how many trips each vehicle can still do this week
    const vehicleState = vehicles.map(v=>({...v, tripsLeft: v.weeklyTrips}));

    // Normalize customers (backward compatible: containers or containersPerDelivery)
    const customers=[...p.customers].map(c=>{
      const ci=validateCoords("Kund "+(c.name||c.id), c);
      if(ci) issues.push({type:"DATA", message:ci, customerId:c.id});
      const allowed=(c.allowedDays && c.allowedDays.length ? c.allowedDays : DAYS).filter(d=>DAYS.includes(d));
      const perDelivery = safeNum((c.containersPerDelivery!=null ? c.containersPerDelivery : c.containers), 0);
      return {
        ...c,
        id: String(c.id||"").trim() || ("CUST-"+uid().slice(0,4)),
        name: (c.name!=null && String(c.name).trim()) ? String(c.name).trim() : String(c.id||"Kund"),
        containersPerDelivery:clamp(perDelivery,0,100000),
        deliveriesPerWeek:clamp(safeNum(c.deliveriesPerWeek,1),1,10),
        allowedDays: allowed,
        minWeekdaysBetween:clamp(safeNum(c.minWeekdaysBetween,0),0,4),
        serviceMinutes:clamp(safeNum(c.serviceMinutes,10),0,600),
      };
    });

    if(issues.some(x=>x.type==="DATA")) return {ok:false, issues, routes:null};

    // Build jobs (one per delivery). This fixes the "same stop appears twice" bug.
    const dayAssignments=Object.fromEntries(DAYS.map(d=>[d,[]]));
    const customerByIdEarly=new Map(customers.map(c=>[c.id,c]));

    function chooseBestDeliveryDays(customer){
      const need = safeNum(customer.deliveriesPerWeek,1);
      const allowed = [...new Set((customer.allowedDays||[]).filter(d=>DAYS.includes(d)))];
      if(need > allowed.length) return null;
      const combos = combinations(allowed, need).filter(combo=>{
        for(let i=0;i<combo.length;i++){
          for(let j=i+1;j<combo.length;j++){
            if(weekdaysBetween(combo[i], combo[j]) < safeNum(customer.minWeekdaysBetween,0)) return false;
          }
        }
        return true;
      });
      if(!combos.length) return null;

      let best=null;
      for(const combo of combos){
        let loadScore=0;
        let clusterScore=0;
        let emptyDayPenalty=0;
        for(const day of combo){
          const assigned = dayAssignments[day] || [];
          loadScore += assigned.reduce((sum,a)=>{
            const cc = customerByIdEarly.get(a.customerId);
            return sum + safeNum(cc && cc.containersPerDelivery, 0);
          }, 0);
          const centroid = averageCoordForAssignments(assigned, customerByIdEarly);
          if(centroid){
            clusterScore += haversineKm({lat:customer.lat, lon:customer.lon}, centroid);
          } else {
            emptyDayPenalty += 1;
            clusterScore += 35;
          }
        }
        const score = (loadScore * 0.6) + (clusterScore * 6) + (emptyDayPenalty * 90);
        if(!best || score < best.score) best = {days: combo, score};
      }
      return best ? best.days : null;
    }

    const customerGroups=customers
      .map(c=>({customer:c, score:customerTightnessScore(c)}))
      .sort((a,b)=>b.score-a.score);

    for(const g of customerGroups){
      const c=g.customer;
      const chosenDays = chooseBestDeliveryDays(c);
      if(!chosenDays){
        issues.push({type:"INFEASIBLE", message:`Kund "${c.name}" kan inte schemaläggas med nuvarande veckodagar/minsta avstånd.`, constraint:"Day scheduling", customerId:c.id});
        continue;
      }
      chosenDays.forEach((day, idx)=>{
        dayAssignments[day].push({customerId:c.id, occ:idx, jobId:`${c.id}__${idx}`});
      });
    }
    if(issues.some(x=>x.type==="INFEASIBLE")) return {ok:false, issues, routes:{routesByDay:{}}};

    const depotNode={id:"DEPOT", lat:p.depot.lat, lon:p.depot.lon};
    const startTimeMin=minutesFromHHMM(p.settings.startTime)||420;
    const overCap=clamp(safeNum(p.settings.allowOverCap,0),0,50);

    function buildRouteSequence(vehicle, pickedJobs, opts={}){
      const stops=pickedJobs.map(j=>{
        const c=j.customer;
        return {
          id:j.jobId, // unique per delivery
          customerId:c.id,
          name:c.name,
          address:c.address,
          lat:c.lat, lon:c.lon,
          containersPerDelivery:c.containersPerDelivery,
          serviceMinutes:c.serviceMinutes,
          twStart:c.timeWindowStart?minutesFromHHMM(c.timeWindowStart):null,
          twEnd:c.timeWindowEnd?minutesFromHHMM(c.timeWindowEnd):null,
        };
      });

      const nodes=[depotNode, ...stops.map(s=>({id:s.id,lat:s.lat,lon:s.lon}))];
      const dist=buildDistanceMatrix(nodes);
      const ignoreTW = !!opts.ignoreTimeWindows;

      function simulateOrder(order){
        let minPrefix = 0;
        let latestDeparture = Number.POSITIVE_INFINITY;
        let prevId = "DEPOT";
        for(const stop of order){
          minPrefix += estimateTravelMinutes(dist[prevId][stop.id], vehicle.meanSpeedKmh);
          if(stop.twEnd!=null) latestDeparture = Math.min(latestDeparture, stop.twEnd - minPrefix);
          minPrefix += safeNum(stop.serviceMinutes,0);
          prevId = stop.id;
        }
        let departure = startTimeMin;
        if(Number.isFinite(latestDeparture)) departure = Math.max(startTimeMin, Math.floor(latestDeparture));

        let t=departure;
        let currentId="DEPOT";
        const ordered=[];
        let twViolations=0;
        for(const stop of order){
          const km=dist[currentId][stop.id];
          const travelMin=estimateTravelMinutes(km, vehicle.meanSpeedKmh);
          const arrival=t+travelMin;
          let wait=0;
          let feasible=true;
          if(stop.twStart!=null && arrival < stop.twStart) wait = stop.twStart-arrival;
          const eta = arrival + wait;
          if(stop.twEnd!=null && eta > stop.twEnd){ feasible=false; twViolations++; }
          if(!ignoreTW && !feasible) return {ok:false, reason:`Tidsfönster infeasible för ett stopp (kontrollera tidsfönster).`};
          t = eta + safeNum(stop.serviceMinutes,0);
          ordered.push({...stop, travelKm:km, travelMin, waitMin:wait, eta});
          currentId = stop.id;
        }
        const backKm=dist[currentId]["DEPOT"];
        const backMin=estimateTravelMinutes(backKm, vehicle.meanSpeedKmh);
        const travelKm=ordered.reduce((s,x)=>s+(x.travelKm||0),0)+backKm;
        const travelMin=ordered.reduce((s,x)=>s+(x.travelMin||0),0)+backMin;
        const waitMin=ordered.reduce((s,x)=>s+(x.waitMin||0),0);
        const serviceMin=ordered.reduce((s,x)=>s+(x.serviceMinutes||0),0);
        const totalMin=travelMin+waitMin+serviceMin;
        const containers=ordered.reduce((s,x)=>s+safeNum(x.containersPerDelivery,0),0);
        const totalCapacity=vehicleTotalCapacity(vehicle);
        const capUsedPct=totalCapacity>0 ? Math.round((containers/totalCapacity)*100) : 0;
        return {ok:true, orderedStops:ordered, totals:{travelKm, travelMin, waitMin, serviceMin, totalMin, containers, capUsedPct, timeWindowViolations:twViolations, departureMin:departure, returnMin:departure+totalMin}};
      }

      function compareSolutions(a,b){
        if(!a) return 1;
        if(!b) return -1;
        const af=!!a.ok, bf=!!b.ok;
        if(af!==bf) return af ? -1 : 1;
        const av=a.totals||{}, bv=b.totals||{};
        if((av.timeWindowViolations||0)!==(bv.timeWindowViolations||0)) return (av.timeWindowViolations||0)-(bv.timeWindowViolations||0);
        if((av.totalMin||1e9)!==(bv.totalMin||1e9)) return (av.totalMin||1e9)-(bv.totalMin||1e9);
        if((av.waitMin||1e9)!==(bv.waitMin||1e9)) return (av.waitMin||1e9)-(bv.waitMin||1e9);
        return (av.travelKm||1e9)-(bv.travelKm||1e9);
      }

      function greedyOrder(mode){
        let currentId="DEPOT";
        let currentTime=startTimeMin;
        const remaining=[...stops];
        const order=[];
        while(remaining.length){
          remaining.sort((a,b)=>{
            const aKm=dist[currentId][a.id], bKm=dist[currentId][b.id];
            const aTravel=estimateTravelMinutes(aKm, vehicle.meanSpeedKmh), bTravel=estimateTravelMinutes(bKm, vehicle.meanSpeedKmh);
            const aArr=currentTime+aTravel, bArr=currentTime+bTravel;
            const aStart=(a.twStart!=null?Math.max(aArr,a.twStart):aArr), bStart=(b.twStart!=null?Math.max(bArr,b.twStart):bArr);
            const aEnd=(a.twEnd!=null?a.twEnd:999999), bEnd=(b.twEnd!=null?b.twEnd:999999);
            const aSlack=aEnd-aStart, bSlack=bEnd-bStart;
            if(mode==="time"){ 
              if((a.twEnd!=null)!==(b.twEnd!=null)) return a.twEnd!=null ? -1 : 1;
              if(aEnd!==bEnd) return aEnd-bEnd;
              if(aSlack!==bSlack) return aSlack-bSlack;
              return aTravel-bTravel;
            }
            if(mode==="distance"){
              if(aTravel!==bTravel) return aTravel-bTravel;
              if((a.twEnd!=null)!==(b.twEnd!=null)) return a.twEnd!=null ? -1 : 1;
              return aEnd-bEnd;
            }
            if((a.twEnd!=null)!==(b.twEnd!=null)) return a.twEnd!=null ? -1 : 1;
            if(aSlack!==bSlack) return aSlack-bSlack;
            return aTravel-bTravel;
          });
          const picked=remaining.shift();
          order.push(picked);
          const travel=estimateTravelMinutes(dist[currentId][picked.id], vehicle.meanSpeedKmh);
          const arrival=currentTime+travel;
          const start=(picked.twStart!=null?Math.max(arrival,picked.twStart):arrival);
          currentTime=start+safeNum(picked.serviceMinutes,0);
          currentId=picked.id;
        }
        return order;
      }

      let best=null;
      if(stops.length<=8){
        const used=new Set();
        function dfs(cur){
          if(cur.length===stops.length){
            const sim=simulateOrder(cur);
            if(compareSolutions(best, sim)>0) best=sim;
            return;
          }
          const remainingStops=stops.filter(s=>!used.has(s.id));
          remainingStops.sort((a,b)=>{
            const aHas=a.twEnd!=null?0:1, bHas=b.twEnd!=null?0:1;
            if(aHas!==bHas) return aHas-bHas;
            const aEnd=a.twEnd!=null?a.twEnd:999999, bEnd=b.twEnd!=null?b.twEnd:999999;
            if(aEnd!==bEnd) return aEnd-bEnd;
            return dist[cur.length?cur[cur.length-1].id:"DEPOT"][a.id]-dist[cur.length?cur[cur.length-1].id:"DEPOT"][b.id];
          });
          for(const stop of remainingStops){
            used.add(stop.id); cur.push(stop); dfs(cur); cur.pop(); used.delete(stop.id);
          }
        }
        dfs([]);
      } else {
        for(const mode of ["time","hybrid","distance"]){
          const sim=simulateOrder(greedyOrder(mode));
          if(compareSolutions(best, sim)>0) best=sim;
        }
      }

      return best || {ok:false, reason:`Ingen möjlig nästa stopp.`};
    }

    const customerById=new Map(customers.map(c=>[c.id,c]));
    const routesByDay=Object.fromEntries(DAYS.map(d=>[d,[]]));

    for(const day of DAYS){
      // Convert today's assignments to delivery-jobs with unique jobId
      let remaining = (dayAssignments[day]||[])
        .map(j=>({ ...j, customer: customerById.get(j.customerId) }))
        .filter(j=>j.customer)
        .sort((a,b)=>customerTightnessScore(b.customer)-customerTightnessScore(a.customer));

      while(remaining.length){
        const vehicle = vehicleState.find(v=>v.tripsLeft>0);
        if(!vehicle){
          issues.push({type:"INFEASIBLE", message:`Dag ${day}: inga fordon med återstående turer denna vecka (weekly trips).`, constraint:"Weekly trips"});
          break;
        }

        const limit = vehicleTotalCapacity(vehicle) + overCap;
        const picked=[]; let used=0;

        for(const job of remaining){
          const c=job.customer;
          if(c.vehicleAllowedIds && c.vehicleAllowedIds.length && !c.vehicleAllowedIds.includes(vehicle.id)) continue;
          const add = safeNum(c.containersPerDelivery,0);
          if(used + add > limit) continue;
          picked.push(job);
          used += add;
        }

        if(!picked.length){
          // Create a preview "not possible" route: pick the closest (smallest over-capacity) single job to show what it would look like.
          const first = remaining[0];
          if(first){
            const prev = buildRouteSequence(vehicle, [first], {ignoreTimeWindows:true});
            routesByDay[day].push({
              id:uid(),
              day,
              vehicleId:vehicle.id,
              vehicleName:vehicle.name||vehicle.id,
              vehicleHasTrailer:Boolean(vehicle.trailerAttached),
              infeasible:true,
              infeasibleReason:`Kunde inte fylla rutt inom kapacitetsregler – visar ett stopp som förhandsvisning.`,
              overMinutes:null,
              overContainers:null,
              stops:(prev.ok?prev.orderedStops:[]),
              totals:(prev.ok?prev.totals:{travelKm:0,travelMin:0,waitMin:0,serviceMin:0,totalMin:0,containers:0,capUsedPct:0,timeWindowViolations:0})
            });
          }
          issues.push({type:"INFEASIBLE", message:`Dag ${day}: kunde inte tilldela några stopp till ${vehicle.name||vehicle.id}. (förhandsvisning skapad)`, constraint:"Capacity/vehicle"});
          break;
        }

        
        const seq=buildRouteSequence(vehicle, picked);

        // If time windows infeasible, still create a preview route (ignore TW) so the planner can decide if it's "close enough".
        if(!seq.ok){
          const prev=buildRouteSequence(vehicle, picked, {ignoreTimeWindows:true});
          routesByDay[day].push({
            id:uid(),
            day,
            vehicleId:vehicle.id,
            vehicleName:vehicle.name||vehicle.id,
            vehicleHasTrailer:Boolean(vehicle.trailerAttached),
            infeasible:true,
            infeasibleReason:seq.reason,
            overMinutes: null,
            overContainers: null,
            stops:(prev.ok?prev.orderedStops:[]),
            totals:(prev.ok?prev.totals:{travelKm:0,travelMin:0,waitMin:0,serviceMin:0,totalMin:0,containers:0,capUsedPct:0,timeWindowViolations:0})
          });
          issues.push({type:"INFEASIBLE", message:`Dag ${day}, ${vehicle.name||vehicle.id}: ${seq.reason} (förhandsvisning skapad).`, constraint:"Time window"});
        } else {
          const overM = Math.max(0, Math.round(seq.totals.totalMin - vehicle.maxDriveMinutesPerDay));
          const capLimit = vehicleTotalCapacity(vehicle) + overCap;
          const overC = Math.max(0, Math.round(seq.totals.containers - capLimit));

          routesByDay[day].push({
            id:uid(),
            day,
            vehicleId:vehicle.id,
            vehicleName:vehicle.name||vehicle.id,
            vehicleHasTrailer:Boolean(vehicle.trailerAttached),
            infeasible: (overM>0 || overC>0),
            infeasibleReason: (overM>0 ? `Över max körtid med ${overM} min.` : (overC>0 ? `Över kapacitet med ${overC} containers.` : "")),
            overMinutes: overM,
            overContainers: overC,
            stops:seq.orderedStops,
            totals:seq.totals
          });

          if(overM>0){
            issues.push({type:"INFEASIBLE", message:`Dag ${day}, ${vehicle.name||vehicle.id}: max körtid överskrids med ${overM} min (förhandsvisning skapad).`, constraint:"Max driving time"});
          }
          if(overC>0){
            issues.push({type:"INFEASIBLE", message:`Dag ${day}, ${vehicle.name||vehicle.id}: kapacitet överskrids med ${overC} containers (förhandsvisning skapad).`, constraint:"Capacity"});
          }
        }

        // consume one weekly trip
        vehicle.tripsLeft = Math.max(0, vehicle.tripsLeft-1);

        const pickedJobIds=new Set(picked.map(x=>x.jobId));
        remaining = remaining.filter(j=>!pickedJobIds.has(j.jobId));
      }
    }

    if(issues.some(x=>x.type==="INFEASIBLE")) return {ok:false, issues, routes:{routesByDay}};

    const allRoutes=DAYS.flatMap(d=>routesByDay[d]);
    const summary={
      vehiclesUsed:allRoutes.length,
      totalKm:allRoutes.reduce((s,r)=>s+(r.totals.travelKm||0),0),
      totalMinutes:allRoutes.reduce((s,r)=>s+(r.totals.totalMin||0),0),
      avgUtilPct:allRoutes.length ? Math.round(allRoutes.reduce((s,r)=>s+(r.totals.capUsedPct||0),0)/allRoutes.length) : 0
    };
    return {ok:true, issues, routes:{routesByDay, summary}};
  }

  const $ = (id)=>document.getElementById(id);

  // --- Map (Leaflet) ---
  let map, depotMarker, customersLayer, routesLayer;
  function ensureMap(){
    if(map) return;
    if(typeof L === "undefined") return; // Leaflet not loaded (offline)
    map = L.map("map", {zoomControl:true});
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap'
    }).addTo(map);
    customersLayer = L.layerGroup().addTo(map);
    routesLayer = L.layerGroup().addTo(map);
  }

  function fitMapToData(){
    if(!map) return;
    const pts=[];
    if(state?.depot?.lat!=null && state?.depot?.lon!=null) pts.push([state.depot.lat, state.depot.lon]);
    (state.customers||[]).forEach(c=>{
      if(c.lat!=null && c.lon!=null) pts.push([c.lat, c.lon]);
    });
    if(pts.length===1){ map.setView(pts[0], 12); return; }
    if(pts.length>1){ map.fitBounds(pts, {padding:[30,30]}); }
  }

  function renderMapStatic(){
    ensureMap();
    if(!map) return;
    customersLayer.clearLayers();
    routesLayer.clearLayers();

    // depot
    const d=state.depot;
    if(d?.lat!=null && d?.lon!=null){
      if(depotMarker) depotMarker.remove();
      depotMarker = L.marker([d.lat, d.lon]).addTo(map).bindPopup(`<b>Depå</b><br>${(d.address||"")}`);
    }

    // customers markers
    (state.customers||[]).forEach(c=>{
      if(c.lat==null || c.lon==null) return;
      const m=L.circleMarker([c.lat, c.lon], {radius:7, weight:2}).addTo(customersLayer);
      m.bindPopup(`<b>${escapeHtml(c.name||c.id)}</b><br>${escapeHtml(c.address||"")}<br>${safeNum(c.containersPerDelivery ?? c.containers,0)} cont/leverans`);
    });

    fitMapToData();
  }

  
function drawRouteOnMap(route){
    ensureMap();
    if(!map || !route) return;
    routesLayer.clearLayers();

    const pts=[];
    const d=state.depot;
    const depotPt = (d?.lat!=null && d?.lon!=null) ? [d.lat, d.lon] : null;
    if(depotPt) pts.push(depotPt);

    // Numbered markers for each stop
    let i=1;
    (route.stops||[]).forEach(s=>{
      if(s.lat==null || s.lon==null) return;
      const pt=[s.lat, s.lon];
      pts.push(pt);
      const icon = L.divIcon({className:"", html:`<div class="numIcon">${i}</div>`, iconSize:[28,28], iconAnchor:[14,14]});
      L.marker(pt, {icon}).addTo(routesLayer)
        .bindPopup(`<b>${escapeHtml(s.name||"")}</b><br>${escapeHtml(s.address||"")}<br>ETA: ${hhmmFromMinutes(s.eta||0)}`);
      i++;
    });

    if(depotPt) pts.push(depotPt);

    if(pts.length>=2){
      L.polyline(pts, {weight:4}).addTo(routesLayer);
      map.fitBounds(pts, {padding:[40,40]});
    }
  }


  function setView(view){
    $("tabData").classList.toggle("active", view==="data");
    $("tabPlan").classList.toggle("active", view==="plan");
    $("viewData").style.display = view==="data" ? "" : "none";
    $("viewPlan").style.display = view==="plan" ? "" : "none";
    if(view==="plan"){ setTimeout(()=>renderMapStatic(), 0); }
  }

  function render(){
    $("depotAddress").value = state.depot.address || "";
    $("depotLat").value = state.depot.lat ?? "";
    $("depotLon").value = state.depot.lon ?? "";

    const r = state.lastRoutes && state.lastRoutes.result;
    const box = $("statusBox");
    if(!r){
      box.className="notice";
      box.textContent="Ingen plan ännu. Klicka “Generera rutter”.";
    } else if(r.ok){
      box.className="notice ok";
      box.textContent="OK: Planeringen är genomförbar utan att bryta hårda constraints.";
    } else {
      box.className="notice bad";
      box.textContent="Problem: Se Planering-fliken för fel/constraints.";
    }

    // vehicles
    const vList=$("vehiclesList"); vList.innerHTML="";
    (state.vehicles||[]).forEach(v=>{
      const div=document.createElement("div");
      div.className="item";

      div.innerHTML = `
        <div class="itemhead">
          <div>
            <div class="itemtitle">${(v.name||v.id)}</div>
            <div class="small">ID: ${v.id} · Lastbil/släp, kapacitet, hastighet, max tid/dag, turer/vecka</div>
          </div>
          <button class="btn danger" data-del-veh="${v.id}">Ta bort</button>
        </div>
        <div style="height:10px"></div>
        <div class="cols3">
          <div class="field"><label>Kapacitet lastbil (containers)</label><input type="number" data-veh="${v.id}" data-k="capacityContainers" value="${v.capacityContainers}"></div>
          <div class="field"><label>Släp kapacitet (containers)</label><input type="number" data-veh="${v.id}" data-k="trailerCapacityContainers" value="${v.trailerCapacityContainers ?? 0}"></div>
          <div class="field"><label>Medelhastighet (km/h)</label><input type="number" data-veh="${v.id}" data-k="meanSpeedKmh" value="${v.meanSpeedKmh}"></div>
          <div class="field"><label>Max tid/dag (min)</label><input type="number" data-veh="${v.id}" data-k="maxDriveMinutesPerDay" value="${v.maxDriveMinutesPerDay}"></div>
          <div class="field"><label>Turer/vecka</label><input type="number" data-veh="${v.id}" data-k="weeklyTrips" value="${v.weeklyTrips ?? 4}"></div>
          <div class="field"><label>Total kapacitet</label><input type="text" value="${vehicleTotalCapacity(v)}" disabled></div>
          <div class="field" style="grid-column:1/-1">
            <label style="display:flex;align-items:center;gap:10px;font-weight:800">
              <input type="checkbox" data-veh-check="${v.id}" data-k="trailerAttached" ${v.trailerAttached ? "checked" : ""} style="width:auto"/>
              Lastbil med släp
            </label>
          </div>
        </div>
      `;
      vList.appendChild(div);
    });

    // customers
    const cList=$("customersList"); cList.innerHTML="";
    const allVehicleIds=(state.vehicles||[]).map(v=>v.id);
    (state.customers||[]).forEach(c=>{
      const isFixed = safeNum(c.deliveriesPerWeek,1) === (c.allowedDays?.length||0);
      const daysHtml = DAYS.map(d=>{
        const checked=(c.allowedDays||[]).includes(d) ? "checked" : "";
        return `<label class="chip" style="cursor:pointer"><input type="checkbox" data-cust="${c.id}" data-day="${d}" ${checked}/> ${d}</label>`;
      }).join(" ");
      const vehHtml = allVehicleIds.length ? allVehicleIds.map(vid=>{
        const checked=(c.vehicleAllowedIds||[]).includes(vid) ? "checked" : "";
        return `<label class="chip" style="cursor:pointer"><input type="checkbox" data-cust="${c.id}" data-veh="${vid}" ${checked}/> ${vid}</label>`;
      }).join(" ") : `<span class="small">Lägg till fordon först</span>`;

      const div=document.createElement("div");
      div.className="item";
      div.id = "cust-"+c.id;
      div.innerHTML = `
        <div class="itemhead">
          <div>
            <div class="itemtitle">
              <input style="max-width:280px" data-cust="${c.id}" data-k="name" value="${(c.name||"").replaceAll('"','&quot;')}"/>
              <span class="chip" style="margin-left:8px">${isFixed ? "Fast" : "Flex"}</span>
            </div>
            <div class="small">ID: ${c.id}</div>
          </div>
          <button class="btn danger" data-del-cust="${c.id}">Ta bort</button>
        </div>
        <div style="height:10px"></div>
        <div class="cols3">
          <div class="field"><label>Adress</label><input data-cust="${c.id}" data-k="address" value="${(c.address||"").replaceAll('"','&quot;')}"/>
            <div style="height:6px"></div>
            <button class="btn" type="button" data-geocode-cust="${c.id}">Hämta koordinater</button></div>
          <div class="cols2">
            <div class="field"><label>Lat</label><input type="number" step="any" data-cust="${c.id}" data-k="lat" value="${c.lat ?? ""}"/></div>
            <div class="field"><label>Lon</label><input type="number" step="any" data-cust="${c.id}" data-k="lon" value="${c.lon ?? ""}"/></div>
          </div>
          <div class="field"><label>Containers</label><input type="number" data-cust="${c.id}" data-k="containersPerDelivery" value="${c.containersPerDelivery ?? c.containers ?? 0}"/></div>

          <div class="field"><label>Leveranser/vecka</label><input type="number" data-cust="${c.id}" data-k="deliveriesPerWeek" value="${c.deliveriesPerWeek}"/></div>
          <div class="field"><label>Min vardagar mellan</label><input type="number" data-cust="${c.id}" data-k="minWeekdaysBetween" value="${c.minWeekdaysBetween}"/></div>
          <div class="field"><label>Servicetid (min)</label><input type="number" data-cust="${c.id}" data-k="serviceMinutes" value="${c.serviceMinutes}"/></div>

          <div class="field"><label>Tidsfönster start</label><input type="time" data-cust="${c.id}" data-k="timeWindowStart" value="${c.timeWindowStart||""}"/></div>
          <div class="field"><label>Tidsfönster slut</label><input type="time" data-cust="${c.id}" data-k="timeWindowEnd" value="${c.timeWindowEnd||""}"/></div>
          <div></div>

          <div class="field" style="grid-column:1/-1">
            <label>Tillåtna dagar</label>
            <div style="display:flex;flex-wrap:wrap;gap:8px">${daysHtml}</div>
          </div>
          <div class="field" style="grid-column:1/-1">
            <label>Fordonsbegränsning (om tomt = alla)</label>
            <div style="display:flex;flex-wrap:wrap;gap:8px">${vehHtml}</div>
          </div>
        </div>
      `;
      cList.appendChild(div);
    });

    renderPlan();
  }

  function renderPlan(){
    const r = state.lastRoutes && state.lastRoutes.result;
    $("planSummary").innerHTML="";
    $("planIssues").innerHTML="";
    $("planRoutes").innerHTML="";

    if(!r){
      $("planIssues").innerHTML = '<div class="small">Klicka “Generera rutter” för att skapa en plan.</div>';
      return;
    }
    const summary=r.routes && r.routes.summary;
    if(summary){
      const items=[["Fordon/rutter", summary.vehiclesUsed],["Total distans", summary.totalKm.toFixed(1)+" km"],["Total tid", Math.round(summary.totalMinutes)+" min"],["Snitt nyttjande", summary.avgUtilPct+"%"]];
      items.forEach(([k,v])=>{
        const d=document.createElement("div");
        d.className="notice";
        d.innerHTML=`<div class="small">${k}</div><div style="font-size:18px;font-weight:900">${v}</div>`;
        $("planSummary").appendChild(d);
      });
    }

    const issues=r.issues||[];
    if(issues.length){
      const div=document.createElement("div");
      div.className="notice bad";
      div.innerHTML='<div style="font-weight:900;margin-bottom:6px">Problem / fel</div>' + issues.map(x=>{const cust=x.customerId?` <span class="link" data-jump-cust="${x.customerId}">(öppna kund)</span>`:""; return `<div>• ${x.message}${x.constraint?` (${x.constraint})`:""}${cust}</div>`;}).join("");
      $("planIssues").appendChild(div);
    } else {
      const div=document.createElement("div");
      div.className="notice ok";
      div.textContent="Planeringen är genomförbar utan att bryta hårda constraints.";
      $("planIssues").appendChild(div);
    }

    const byDay=(r.routes && r.routes.routesByDay) || {};
    for(const day of DAYS){
      for(const route of (byDay[day]||[])){
        const card=document.createElement("div");
        card.className="item";
        const header=`<div class="row" style="justify-content:space-between"><div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
          <div class="itemtitle">${day} · ${(route.vehicleName||route.vehicleId)}</div>
          <span class="chip">${route.totals.capUsedPct}% kapacitet</span><span class="chip">${route.vehicleName || route.vehicleId}${route.vehicleHasTrailer ? " · med släp" : ""}</span>${route.infeasible?` <span class="chip" style="border-color:var(--danger);color:var(--danger);background:#fff5f5">EJ MÖJLIG</span>`:""}
          <span class="chip">${route.totals.travelKm.toFixed(1)} km</span>
          <span class="chip">${Math.round(route.totals.totalMin)} min</span>${route.overMinutes?` <span class="chip" style="border-color:var(--danger);color:var(--danger);background:#fff5f5">+${route.overMinutes} min</span>`:""}${route.overContainers?` <span class="chip" style="border-color:var(--danger);color:var(--danger);background:#fff5f5">+${route.overContainers} cont</span>`:""}
          ${route.totals.departureMin!=null?`<span class="chip">start ${hhmmFromMinutes(route.totals.departureMin)}</span>`:""}
          ${route.totals.returnMin!=null?`<span class="chip">retur ${hhmmFromMinutes(route.totals.returnMin)}</span>`:""}
          <span class="chip">väntan ${Math.round(route.totals.waitMin)} min</span>
        </div><div style="display:flex;gap:8px;align-items:center">
            <button class="btn" data-regenerate="1">Generera om</button>
          </div></div>`;
        const rows=(route.stops||[]).map((s,i)=>`
          <tr>
            <td>${i+1}</td>
            <td><div style="font-weight:900">${s.name}</div><div class="small">${s.address||""}</div></td>
            <td>${hhmmFromMinutes(s.eta)}</td>
            <td>${(s.twStart!=null && s.twEnd!=null) ? (hhmmFromMinutes(s.twStart)+"–"+hhmmFromMinutes(s.twEnd)) : "–"}</td>
            <td>${s.containersPerDelivery}</td>
            <td>${s.serviceMinutes} min</td>
            <td>${s.waitMin} min</td>
            <td>${(s.travelKm||0).toFixed(2)} km</td>
          </tr>`).join("");
        card.innerHTML = header + `${route.infeasible && route.infeasibleReason ? `<div class="notice bad" style="margin-top:10px">Ej möjlig rutt: ${route.infeasibleReason}</div>`:""}` + `<div style="height:10px"></div>
          <div style="overflow:auto;border:1px solid var(--border);border-radius:14px">
            <table>
              <thead><tr><th>#</th><th>Kund</th><th>ETA</th><th>Tidsfönster</th><th>Containers</th><th>Service</th><th>Väntan</th><th>Dist (prev)</th></tr></thead>
              <tbody>${rows}</tbody>
            </table>
          </div>`;
        card.style.cursor="pointer";
        card.addEventListener("click", ()=>{ drawRouteOnMap(route); });
        $("planRoutes").appendChild(card);
      }
    }
    if(!$("planRoutes").children.length){
      $("planRoutes").innerHTML = '<div class="small">Inga rutter att visa.</div>';
    }
  }



  function parseCSV(text){
    // Handles comma or semicolon separated values, with basic quoted fields support.
    const lines = text.replace(/\r/g,"").split("\n").filter(l=>l.trim().length);
    if(!lines.length) return {headers:[], rows:[]};
    const sniff = (lines[0].match(/;/g)||[]).length > (lines[0].match(/,/g)||[]).length ? ";" : ",";
    const sep = sniff;
    const readLine=(line)=>{
      const out=[]; let cur=""; let q=false;
      for(let i=0;i<line.length;i++){
        const ch=line[i];
        if(ch==='"'){
          if(q && line[i+1]==='"'){ cur+='"'; i++; }
          else q=!q;
        } else if(ch===sep && !q){
          out.push(cur); cur="";
        } else cur+=ch;
      }
      out.push(cur);
      return out.map(s=>s.trim());
    };
    const headers = readLine(lines[0]).map(h=>h.trim());
    const rows = lines.slice(1).map(l=>readLine(l));
    return {headers, rows};
  }

  function normHeader(h){
    return String(h||"").toLowerCase().trim()
      .replace(/\s+/g,"_")
      .replace(/å/g,"a").replace(/ä/g,"a").replace(/ö/g,"o");
  }

  function downloadText(filename, text, mime="text/plain"){
    const blob=new Blob([text], {type:mime});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url; a.download=filename;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }

  function toBool(x){
    const s=String(x||"").trim().toLowerCase();
    return ["1","true","yes","y","ja"].includes(s);
  }

  function gotoCustomer(customerId){
    if(!customerId) return;
    setView("data");
    // small delay to allow DOM render if needed
    requestAnimationFrame(()=>{
      const el=document.getElementById("cust-"+customerId);
      if(el){
        el.scrollIntoView({behavior:"smooth", block:"start"});
        el.classList.add("focusHint");
        setTimeout(()=>el.classList.remove("focusHint"), 1600);
      }
    });
  }


  function bindEvents(){
    $("tabData").addEventListener("click", ()=>setView("data"));
    $("tabPlan").addEventListener("click", ()=>setView("plan"));

    $("btnFitMap")?.addEventListener("click", ()=>{ renderMapStatic(); });
    $("btnGeocodeDepot")?.addEventListener("click", ()=>{ geocodeDepot(); });

    document.body.addEventListener("click", (e)=>{
      const t=e.target;
      if(t && t.dataset && t.dataset.jumpCust){
        gotoCustomer(t.dataset.jumpCust);
      }
      if(t && t.dataset && t.dataset.regenerate){
        const res=planRoutes(state);
        state.lastRoutes={generatedAt:new Date().toISOString(), result:res};
        save(); render(); setView("plan");
      }
      if(t && t.dataset && t.dataset.geocodeCust){
        geocodeCustomer(t.dataset.geocodeCust);
      }
    });

    $("depotAddress").addEventListener("input", e=>{ state.depot.address=e.target.value; save(); });
    $("depotLat").addEventListener("input", e=>{ state.depot.lat=safeNum(e.target.value, state.depot.lat); save(); });
    $("depotLon").addEventListener("input", e=>{ state.depot.lon=safeNum(e.target.value, state.depot.lon); save(); });

    $("addVehicle").addEventListener("click", ()=>{
      const n=(state.vehicles.length||0)+1;
      state.vehicles.unshift({id:`CAR-${n}`, name:`Lastbil ${n}`, weeklyTrips:4, capacityContainers:60, trailerAttached:false, trailerCapacityContainers:0, meanSpeedKmh:40, maxDriveMinutesPerDay:480, priority:n});
      save(); render();
    });
    $("addCustomer").addEventListener("click", ()=>{
      const n=(state.customers.length||0)+1;
      state.customers.unshift({id:`CUST-${n}`, name:"Ny kund", address:"", lat:state.depot.lat, lon:state.depot.lon, containersPerDelivery:10,
        deliveriesPerWeek:1, allowedDays:[...DAYS], minWeekdaysBetween:0, timeWindowStart:"", timeWindowEnd:"", serviceMinutes:10, vehicleAllowedIds:[]});
      save(); render();
    });

    document.body.addEventListener("click", (e)=>{
      const t=e.target;
      if(t && t.dataset && t.dataset.delVeh){
        state.vehicles = state.vehicles.filter(v=>v.id!==t.dataset.delVeh);
        save(); render(); return;
      }
      if(t && t.dataset && t.dataset.delCust){
        state.customers = state.customers.filter(c=>c.id!==t.dataset.delCust);
        save(); render(); return;
      }
    });

    document.body.addEventListener("input", (e)=>{
      const t=e.target;
      if(t && t.dataset && t.dataset.veh){
        const v=state.vehicles.find(x=>x.id===t.dataset.veh);
        if(v){
          const numericVehicleKeys=["capacityContainers","trailerCapacityContainers","meanSpeedKmh","maxDriveMinutesPerDay","weeklyTrips","priority"];
          const key=t.dataset.k;
          v[key]=numericVehicleKeys.includes(key) ? safeNum(t.value, v[key]) : t.value;
          save(); render();
        }
      }
      if(t && t.dataset && t.dataset.cust && t.dataset.k){
        const c=state.customers.find(x=>x.id===t.dataset.cust);
        if(c){
          const k=t.dataset.k;
          if(["lat","lon","containers","deliveriesPerWeek","minWeekdaysBetween","serviceMinutes","containersPerDelivery"].includes(k)) c[k]=safeNum(t.value, c[k]);
          else c[k]=t.value;
          save();
        }
      }
    });

    document.body.addEventListener("change", (e)=>{
      const t=e.target;
      if(t && t.dataset && t.dataset.vehCheck){
        const v=state.vehicles.find(x=>x.id===t.dataset.vehCheck);
        if(v){
          v[t.dataset.k]=!!t.checked;
          save(); render();
        }
      }
      if(t && t.dataset && t.dataset.cust && t.dataset.day){
        const c=state.customers.find(x=>x.id===t.dataset.cust);
        if(c){
          const set=new Set(c.allowedDays||[]);
          if(t.checked) set.add(t.dataset.day); else set.delete(t.dataset.day);
          c.allowedDays=[...set]; save(); render();
        }
      }
      if(t && t.dataset && t.dataset.cust && t.dataset.veh){
        const c=state.customers.find(x=>x.id===t.dataset.cust);
        if(c){
          const set=new Set(c.vehicleAllowedIds||[]);
          if(t.checked) set.add(t.dataset.veh); else set.delete(t.dataset.veh);
          c.vehicleAllowedIds=[...set]; save(); render();
        }
      }
    });

    $("btnGenerate").addEventListener("click", ()=>{
      const res=planRoutes(state);
      state.lastRoutes={generatedAt:new Date().toISOString(), result:res};
      save(); render(); setView("plan");
    });

    $("btnExport").addEventListener("click", ()=>{
      const blob=new Blob([JSON.stringify(state,null,2)], {type:"application/json"});
      const url=URL.createObjectURL(blob);
      const a=document.createElement("a");
      a.href=url; a.download="tvatteri_routeplanner_project.json";
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    });


    $("btnExportCsv").addEventListener("click", ()=>{
      const r = state.lastRoutes && state.lastRoutes.result;
      const byDay = r && r.routes && r.routes.routesByDay;
      if(!byDay){ alert("Inga rutter att exportera. Generera rutter först."); return; }
      const rows=[];
      rows.push(["day","vehicle","stop_order","customer_id","customer_name","address","lat","lon","eta","time_window","containers_per_delivery","service_minutes","wait_minutes","travel_km_from_prev"]);
      for(const day of DAYS){
        for(const route of (byDay[day]||[])){
          const veh = route.vehicleName || route.vehicleId || "";
          (route.stops||[]).forEach((s,i)=>{
            const tw = (s.twStart!=null && s.twEnd!=null) ? (hhmmFromMinutes(s.twStart)+"-"+hhmmFromMinutes(s.twEnd)) : "";
            rows.push([
              day, veh, String(i+1),
              s.customerId||"", s.name||"", s.address||"",
              s.lat??"", s.lon??"",
              hhmmFromMinutes(s.eta||0),
              tw,
              String(s.containersPerDelivery??""),
              String(s.serviceMinutes??""),
              String(s.waitMin??""),
              String((s.travelKm||0).toFixed(3))
            ]);
          });
        }
      }
      const csv = rows.map(r=>r.map(x=>{
        const s=String(x??"");
        return /[",\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s;
      }).join(",")).join("\n");
      const blob=new Blob([csv], {type:"text/csv;charset=utf-8"});
      const url=URL.createObjectURL(blob);
      const a=document.createElement("a");
      a.href=url; a.download="tvatteri_routes.csv";
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    });


    $("btnDownloadTemplates").addEventListener("click", ()=>{
      const cust = [
        ["id","name","address","lat","lon","containersPerDelivery","deliveriesPerWeek","allowedDays","minWeekdaysBetween","timeWindowStart","timeWindowEnd","serviceMinutes","vehicleAllowedIds"],
        ["CUST-1","Nissastigen","Exempeladress 1","57.708","11.974","18","2","Mon;Thu;Fri","1","09:00","12:00","20",""],
      ].map(r=>r.join(",")).join("\n");
      const veh = [
        ["id","name","capacityContainers","trailerAttached","trailerCapacityContainers","meanSpeedKmh","maxDriveMinutesPerDay","weeklyTrips","priority"],
        ["CAR-1","Lastbil 1","70","false","0","40","480","4","1"],
      ].map(r=>r.join(",")).join("\n");
      downloadText("customers_template.csv", cust, "text/csv;charset=utf-8");
      downloadText("vehicles_template.csv", veh, "text/csv;charset=utf-8");
      alert("CSV-mallar nedladdade (customers_template.csv, vehicles_template.csv).");
    });




    $("importCustomersCsv").addEventListener("change", async (e)=>{
      const file=e.target.files && e.target.files[0];
      if(!file) return;
      const text=await file.text();
      const {headers, rows}=parseCSV(text);
      const H=headers.map(normHeader);
      const idx=(key)=>H.indexOf(normHeader(key));

      const get=(row, key, fallback="")=>{
        const i=idx(key);
        return i>=0 ? (row[i]??fallback) : fallback;
      };

      const newCustomers=[];
      for(const row of rows){
        const id = String(get(row,"id","")).trim() || ("CUST-"+uid().slice(0,4));
        const name = String(get(row,"name","Ny kund")).trim() || id;
        const address = String(get(row,"address","")).trim();
        const lat = safeNum(get(row,"lat",""), state.depot.lat);
        const lon = safeNum(get(row,"lon",""), state.depot.lon);
        const containersPerDelivery = safeNum(get(row,"containersPerDelivery", get(row,"containers","10")), 10);
        const deliveriesPerWeek = safeNum(get(row,"deliveriesPerWeek","1"), 1);
        const allowedDaysRaw = String(get(row,"allowedDays","")).trim();
        const allowedDays = allowedDaysRaw ? allowedDaysRaw.split(/[\s;|]+/).map(x=>x.trim()).filter(Boolean) : [...DAYS];
        const minWeekdaysBetween = safeNum(get(row,"minWeekdaysBetween","0"), 0);
        const timeWindowStart = String(get(row,"timeWindowStart","")).trim();
        const timeWindowEnd = String(get(row,"timeWindowEnd","")).trim();
        const serviceMinutes = safeNum(get(row,"serviceMinutes","10"), 10);
        const vehAllowedRaw = String(get(row,"vehicleAllowedIds","")).trim();
        const vehicleAllowedIds = vehAllowedRaw ? vehAllowedRaw.split(/[\s;|]+/).map(x=>x.trim()).filter(Boolean) : [];

        newCustomers.push({id,name,address,lat,lon,containersPerDelivery,deliveriesPerWeek,allowedDays,minWeekdaysBetween,timeWindowStart,timeWindowEnd,serviceMinutes,vehicleAllowedIds});
      }

      // Merge: replace by id if exists, else add
      const byId=new Map((state.customers||[]).map(c=>[c.id,c]));
      for(const c of newCustomers) byId.set(c.id, c);
      state.customers=[...byId.values()];
      save(); render();
      alert(`Importerade/uppdaterade ${newCustomers.length} kunder från CSV.`);
      e.target.value="";
    });

    $("importVehiclesCsv").addEventListener("change", async (e)=>{
      const file=e.target.files && e.target.files[0];
      if(!file) return;
      const text=await file.text();
      const {headers, rows}=parseCSV(text);
      const H=headers.map(normHeader);
      const idx=(key)=>H.indexOf(normHeader(key));
      const get=(row, key, fallback="")=>{
        const i=idx(key);
        return i>=0 ? (row[i]??fallback) : fallback;
      };

      const newVehicles=[];
      for(const row of rows){
        const id = String(get(row,"id","")).trim() || ("CAR-"+uid().slice(0,4));
        const name = String(get(row,"name", id)).trim() || id;
        const capacityContainers = safeNum(get(row,"capacityContainers","60"), 60);
        const trailerAttached = toBool(get(row,"trailerAttached","false"));
        const trailerCapacityContainers = safeNum(get(row,"trailerCapacityContainers","0"), 0);
        const meanSpeedKmh = safeNum(get(row,"meanSpeedKmh","40"), 40);
        const maxDriveMinutesPerDay = safeNum(get(row,"maxDriveMinutesPerDay","480"), 480);
        const weeklyTrips = safeNum(get(row,"weeklyTrips","4"), 4);
        const priority = safeNum(get(row,"priority","1"), 1);
        newVehicles.push({id,name,capacityContainers,trailerAttached,trailerCapacityContainers,meanSpeedKmh,maxDriveMinutesPerDay,weeklyTrips,priority});
      }

      const byId=new Map((state.vehicles||[]).map(v=>[v.id,v]));
      for(const v of newVehicles) byId.set(v.id, v);
      state.vehicles=[...byId.values()];
      save(); render();
      alert(`Importerade/uppdaterade ${newVehicles.length} fordon från CSV.`);
      e.target.value="";
    });


    $("importFile").addEventListener("change", (e)=>{
      const f=e.target.files && e.target.files[0];
      if(!f) return;
      const reader=new FileReader();
      reader.onload=()=>{
        try{
          const obj=JSON.parse(String(reader.result||""));
          if(obj && typeof obj==="object"){ state=obj; save(); render(); setView("data"); }
        }catch{ alert("Import misslyckades: ogiltig JSON"); }
      };
      reader.readAsText(f);
      e.target.value="";
    });

    $("btnReset").addEventListener("click", ()=>{
      state=demoProject(); save(); render(); setView("data");
    });
  }

  try{
    load(); save(); bindEvents(); render();
  }catch(err){
    document.body.innerHTML = "<pre style='padding:16px;color:#b91c1c'>Appen kraschade: "+String(err)+"\n\nÖppna Console (F12) och skicka feltexten.</pre>";
    console.error(err);
  }
</script>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
          integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

</body>
</html>
