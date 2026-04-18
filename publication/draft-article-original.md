# ANALISIS PERFORMA DAN FAULT TOLERANCE STRATEGI LOAD BALANCING PADA ARSITEKTUR MICROSERVICES

**Running Title**: Analisis Performa dan Fault Tolerance Load Balancing Microservices

---

## ABSTRAK

**Latar Belakang**: Arsitektur microservices telah menjadi paradigma dominan dalam pengembangan aplikasi modern, namun distribusi beban yang optimal antar layanan dan resilience terhadap failures masih menjadi tantangan signifikan. **Tujuan**: Penelitian ini bertujuan untuk menganalisis performa dan fault tolerance tiga strategi load balancing (Round Robin, Least Connection, dan Weighted Round Robin) dalam konteks arsitektur microservices. **Metode**: Penelitian eksperimental dilakukan dengan mengimplementasikan sistem e-commerce berbasis microservices menggunakan Node.js dan NGINX sebagai load balancer. Pengujian dilakukan pada tiga tingkat beban (rendah: 10–20 req/s, sedang: 25–50 req/s, tinggi: 50–100 req/s) dengan tiga kali replikasi untuk setiap kondisi guna menyeimbangkan validitas statistik dengan kelayakan eksperimental. Evaluasi fault tolerance dilakukan melalui controlled failure injection. Metrik yang diukur meliputi response time (median, P95, P99), throughput (requests per second), success rate, dan resilience under failures. **Hasil**: Hasil menunjukkan bahwa pada kondisi normal, ketiga strategi memberikan performa median response time yang sebanding (perbedaan < 5 ms pada beban rendah–sedang). Perbedaan signifikan muncul pada tail latency (P99) di beban tinggi, dengan Weighted Round Robin menunjukkan P99 terendah (292.2 ± 13.7 ms) diikuti Least Connection (313.1 ± 54.7 ms) dan Round Robin (361.0 ± 67.4 ms). Evaluasi fault tolerance menunjukkan perbedaan paling dramatis: pada dual service failure (50% capacity loss), P99 Round Robin melonjak dari 284 ms ke 2.636 ms (peningkatan 827%), sementara Least Connection dan Weighted Round Robin tetap stabil (perubahan < 1%). Mean response time Round Robin meningkat 42% (126 ms → 180 ms), sedangkan Least Connection dan Weighted Round Robin tidak menunjukkan perubahan signifikan. **Kesimpulan**: Pemilihan strategi load balancing memiliki dampak terbesar pada resilience terhadap failures. Least Connection dan Weighted Round Robin direkomendasikan untuk production systems yang memerlukan fault tolerance tinggi, sementara Round Robin memadai untuk lingkungan stabil tanpa risiko failure.

**Kata kunci**: load balancing, microservices, performance evaluation, NGINX, container orchestration, fault tolerance

---

## ABSTRACT

**Background**: Microservices architecture has become the dominant paradigm in modern application development, yet optimal load distribution across services and resilience to failures remain significant challenges. **Objective**: This research aims to analyze the performance and fault tolerance of three load balancing strategies (Round Robin, Least Connection, and Weighted Round Robin) in the context of microservices architecture. **Methods**: An experimental study was conducted by implementing an e-commerce microservices system using Node.js and NGINX as load balancer. Testing was performed under three load levels (low: 10–20 req/s, medium: 25–50 req/s, high: 50–100 req/s) with three replications per condition to balance statistical validity with experimental feasibility. Fault tolerance evaluation was conducted through controlled failure injection. Measured metrics include response time (median, P95, P99), throughput (requests per second), success rate, and resilience under failures. **Results**: Under normal conditions, all three strategies showed comparable median response times (differences < 5 ms at low–medium load). Significant differences emerged in tail latency (P99) under high load, with Weighted Round Robin achieving the lowest P99 (292.2 ± 13.7 ms), followed by Least Connection (313.1 ± 54.7 ms) and Round Robin (361.0 ± 67.4 ms). The most dramatic differentiation appeared in fault tolerance evaluation: under dual service failure (50% capacity loss), Round Robin's P99 latency surged from 284 ms to 2,636 ms (an 827% increase), while Least Connection and Weighted Round Robin remained stable (< 1% change). Round Robin's mean response time increased 42% (126 ms → 180 ms), whereas Least Connection and Weighted Round Robin showed no significant change. **Conclusion**: Load balancing strategy selection has the greatest impact on failure resilience. Least Connection and Weighted Round Robin are recommended for production systems requiring high fault tolerance, while Round Robin is adequate for stable environments with no failure risk.

**Keywords**: load balancing, microservices, performance evaluation, NGINX, container orchestration, fault tolerance

---

## 1. PENDAHULUAN

Transformasi digital telah mendorong evolusi arsitektur perangkat lunak dari monolitik menuju microservices, yang menawarkan skalabilitas, fleksibilitas, dan kemudahan maintenance yang lebih baik (Newman, 2021). Namun, kompleksitas dalam mengelola komunikasi antar layanan dan distribusi beban kerja menjadi tantangan baru yang signifikan (Richardson, 2018). Load balancing menjadi komponen kritis dalam memastikan performa optimal sistem microservices dengan mendistribusikan request secara merata ke multiple service instances (Tanenbaum & Van Steen, 2017).

Berbagai strategi load balancing telah dikembangkan, masing-masing dengan karakteristik dan trade-off yang berbeda. Round Robin (RR) merupakan strategi paling sederhana yang mendistribusikan request secara berurutan, Least Connection (LC) mempertimbangkan jumlah koneksi aktif pada setiap server, dan Weighted Round Robin (WRR) memberikan prioritas berdasarkan kapasitas server. Meskipun strategi-strategi ini telah banyak digunakan, literatur menunjukkan kurangnya studi eksperimental komprehensif yang membandingkan performanya dalam konteks microservices modern, terutama dalam aspek fault tolerance (Di Francesco et al., 2017).

Penelitian sebelumnya mayoritas bersifat teoretis atau menggunakan simulasi (Ghomi et al., 2017), dengan terbatasnya studi yang mengimplementasikan sistem nyata untuk evaluasi empiris. Selain itu, sebagian besar penelitian fokus pada metrik tunggal seperti response time, tanpa mempertimbangkan aspek throughput, scalability, dan fault tolerance secara komprehensif (Taibi et al., 2017). Evaluasi resilience terhadap service failures, yang merupakan kondisi tidak terhindarkan dalam lingkungan production, belum mendapat perhatian memadai dalam literatur.

Berdasarkan gap penelitian yang teridentifikasi, penelitian ini bertujuan untuk menganalisis performa dan fault tolerance tiga strategi load balancing (Round Robin, Least Connection, dan Weighted Round Robin) dalam arsitektur microservices. Secara spesifik, penelitian ini menjawab pertanyaan: (1) Bagaimana performa ketiga strategi dalam hal response time, throughput, dan success rate pada berbagai tingkat beban? (2) Bagaimana pengaruh tingkat beban terhadap performa masing-masing strategi? (3) Bagaimana resilience masing-masing strategi terhadap service failures? dan (4) Strategi mana yang paling optimal untuk kondisi tertentu dalam sistem microservices?

Penelitian ini memberikan kontribusi teoritis berupa bukti empiris komprehensif terkait performa dan fault tolerance load balancing dalam arsitektur microservices, mengisi gap dalam literatur dengan evaluasi eksperimental yang mencakup multiple metrics dan failure scenarios. Secara praktis, penelitian ini memberikan panduan bagi software architects dan DevOps engineers dalam memilih strategi load balancing yang sesuai dengan karakteristik aplikasi, infrastruktur, dan requirement fault tolerance mereka.

Penelitian ini dibatasi pada evaluasi tiga strategi load balancing (Round Robin, Least Connection, dan Weighted Round Robin) yang diimplementasikan menggunakan NGINX sebagai load balancer pada platform containerized Docker. Pengujian dilakukan pada aplikasi microservices berbasis HTTP/REST dalam lingkungan pengujian lokal (single host), yang memungkinkan controlled experiment dengan reproducible results.

---

## 2. TINJAUAN PUSTAKA

### 2.1 Arsitektur Microservices

Microservices merupakan architectural style yang mengorganisasikan aplikasi sebagai kumpulan layanan kecil, loosely coupled, dan independently deployable (Dragoni et al., 2017). Setiap service bertanggung jawab atas business capability spesifik dan dapat di-develop, di-deploy, dan di-scale secara independen (Fowler & Lewis, 2014). 

Keuntungan utama arsitektur microservices meliputi:
- **Scalability**: Setiap service dapat di-scale secara independen sesuai kebutuhan (Jamshidi et al., 2018)
- **Technology diversity**: Setiap team dapat memilih technology stack yang paling sesuai
- **Resilience**: Failure pada satu service tidak menyebabkan total system failure (Balalaie et al., 2016)
- **Faster deployment**: Smaller codebases memungkinkan deployment yang lebih cepat (Thönes, 2015)

Namun, microservices juga membawa kompleksitas baru, termasuk distributed system challenges, network latency, dan kebutuhan akan sophisticated load balancing mechanisms (Kratzke & Quint, 2017).

### 2.2 Load Balancing dalam Distributed Systems

Load balancing adalah teknik untuk mendistribusikan workload secara merata di antara multiple computing resources (Soldani et al., 2018). Tujuan utamanya adalah memaksimalkan throughput, meminimalkan response time, dan menghindari overload pada satu resource tertentu (Randles et al., 2010).

Dalam konteks microservices, load balancing dapat diimplementasikan pada berbagai layer:
- **Client-side load balancing**: Client memilih service instance (Burns, 2018)
- **Server-side load balancing**: Dedicated load balancer mendistribusikan requests (NGINX, 2024)
- **Service mesh**: Infrastructure layer untuk service-to-service communication (Villamizar et al., 2015)

### 2.3 Strategi Load Balancing

#### 2.3.1 Round Robin (RR)

Round Robin mendistribusikan requests secara berurutan ke setiap server dalam rotation (Ghomi et al., 2017). Algoritma ini simple dan memiliki overhead minimal, namun tidak mempertimbangkan current load atau server capacity (Randles et al., 2010).

**Kelebihan**:
- Implementasi sederhana dan overhead rendah
- Distribusi merata pada server homogen
- Cocok untuk requests dengan durasi serupa

**Kekurangan**:
- Tidak adaptive terhadap server load
- Tidak optimal untuk server heterogen
- Performa menurun pada varying request duration

#### 2.3.2 Least Connection (LC)

Least Connection merutekan request ke server dengan jumlah koneksi aktif paling sedikit (NGINX, 2024). Strategi ini lebih adaptive dibanding RR karena mempertimbangkan current server load (Nygard, 2018).

**Kelebihan**:
- Adaptive terhadap server load
- Optimal untuk varying request duration
- Better performance under high load

**Kekurangan**:
- Overhead untuk tracking connections
- Kompleksitas implementasi lebih tinggi
- Potensi thundering herd pada startup

#### 2.3.3 Weighted Round Robin (WRR)

Weighted Round Robin memberikan bobot berbeda pada setiap server berdasarkan kapasitasnya (Ghomi et al., 2017). Server dengan bobot lebih tinggi menerima lebih banyak requests (Gan et al., 2019).

**Kelebihan**:
- Optimal untuk heterogeneous servers
- Configurable berdasarkan server capacity
- Predictable distribution pattern

**Kekurangan**:
- Memerlukan manual configuration
- Tidak adaptive terhadap runtime load
- Kompleks pada dynamic environments

### 2.4 Penelitian Terdahulu

Beberapa penelitian sebelumnya telah mengeksplorasi load balancing dalam berbagai konteks:

**Tabel 1. Penelitian Terdahulu**

| Peneliti | Tahun | Fokus | Metode | Gap |
|----------|-------|-------|--------|-----|
| Ghomi et al. | 2017 | Load balancing algorithms in cloud | Survey | Tidak ada eksperimen langsung |
| Taibi et al. | 2017 | Migrasi ke microservices | Empirical investigation | Fokus pada migrasi, bukan performa LB |
| Di Francesco et al. | 2017 | Architecting microservices | Systematic mapping | Kurang evaluasi performa |
| Randles et al. | 2010 | Distributed LB algorithms | Comparative study | Tidak spesifik microservices |
| Villamizar et al. | 2015 | Monolithic vs microservices | Cloud deployment | Tidak membandingkan strategi LB |

**Gap Penelitian**: Dari analisis literatur, teridentifikasi bahwa:
1. Kurangnya studi eksperimental dengan implementasi nyata
2. Evaluasi performa yang tidak komprehensif (hanya metrik tunggal)
3. Terbatasnya penelitian yang membandingkan multiple strategies secara langsung
4. Kurangnya guideline praktis untuk praktisi industri

**Posisi Penelitian**: Penelitian ini mengisi gap dengan melakukan analisis eksperimental komprehensif yang mengevaluasi performa dan fault tolerance tiga strategi load balancing dengan multiple metrics pada sistem microservices yang diimplementasikan secara nyata.

---

## 3. METODOLOGI

### 3.1 Desain Penelitian

Penelitian ini menggunakan pendekatan eksperimental dengan desain factorial 3×3 (3 strategi × 3 load levels). Setiap kondisi direplikasi 3 kali untuk menyeimbangkan validitas statistik dengan kelayakan eksperimental. Ukuran sampel N=3 memungkinkan perhitungan nilai rata-rata, standar deviasi, dan confidence intervals yang memadai untuk analisis komparatif (Field, 2018), serta merupakan praktik standar dalam penelitian eksperimental computer science (Arcuri & Briand, 2014).

**Tabel 2. Desain Eksperimen**

| Faktor | Level |
|--------|-------|
| Strategi Load Balancing | Round Robin, Least Connection, Weighted RR |
| Load Level | Low (100 users), Medium (500 users), High (1000 users) |
| Replikasi | 3 runs per kondisi (N=3) |
| Total eksperimen performance | 3 × 3 × 3 = 27 runs |
| Total eksperimen fault tolerance | 37 runs (baseline + failure scenarios) |
| **Grand total** | **64 experimental runs** |

### 3.2 Arsitektur Sistem

Sistem yang diimplementasikan merupakan aplikasi e-commerce sederhana berbasis microservices dengan komponen sebagai berikut:
![Gambar 1. Arsitektur Sistem Pengujian Load Balancing pada Microservices](figures/system-architecture.png)

**Gambar 1.** Arsitektur sistem pengujian yang terdiri dari Artillery.io sebagai load generator, NGINX sebagai load balancer, dan 4 Node.js microservice instances dalam Docker containers.

**Spesifikasi Komponen**:

1. **Microservice Layer**
   - Platform: Node.js v18 dengan Express.js framework
   - Jumlah instances: 4 service replicas
   - Endpoints: `/api/products` (GET), `/health` (health check)
   - Processing time: Simulated 50-200ms (random)

2. **Load Balancer Layer**
   - Software: NGINX v1.24
   - Konfigurasi: 3 variasi (RR, LC, WRR)
   - Port: 8080 (external), 3000 (internal service)

3. **Container Platform**
   - Docker Engine v24.0 (Merkel, 2014)
   - Docker Compose untuk orchestration
   - Bridge network untuk service communication

### 3.3 Konfigurasi Load Balancing

#### 3.3.1 Round Robin Configuration
```nginx
upstream backend {
    server service1:3000;
    server service2:3000;
    server service3:3000;
    server service4:3000;
}
```

#### 3.3.2 Least Connection Configuration
```nginx
upstream backend {
    least_conn;
    server service1:3000;
    server service2:3000;
    server service3:3000;
    server service4:3000;
}
```

#### 3.3.3 Weighted Round Robin Configuration
```nginx
upstream backend {
    server service1:3000 weight=3;
    server service2:3000 weight=2;
    server service3:3000 weight=2;
    server service4:3000 weight=1;
}
```

### 3.4 Skenario Pengujian

Pengujian dilakukan menggunakan Artillery.io dengan tiga skenario beban:

**Tabel 3. Skenario Load Testing**

| Skenario | Arrival Rate (req/s) | Total Requests | Duration | Phases |
|----------|---------------------|----------------|----------|--------|
| Low Load | 10–20 | ~3.600 | 4 menit | Warm-up 60s (10/s), Sustained 120s (20/s), Cool-down 60s (10/s) |
| Medium Load | 25–50 | ~12.000 | 5 menit | Warm-up 60s (25/s), Sustained 180s (50/s), Cool-down 60s (25/s) |
| High Load | 50–100 | ~30.000 | 6 menit | Warm-up 60s (50/s), Sustained 240s (100/s), Cool-down 60s (50/s) |

**Request Distribution**:
- GET `/api/products`: 70% (browse products)
- GET `/api/products/:id`: 20% (view product detail)
- GET `/api/products/category/:category`: 10% (filter by category)

### 3.5 Metrik Evaluasi

#### 3.5.1 Response Time
- **Median**: Nilai tengah response time
- **P95**: 95th percentile (95% requests lebih cepat)
- **P99**: 99th percentile (99% requests lebih cepat)
- **Min/Max**: Response time minimum dan maksimum

#### 3.5.2 Throughput
- **Requests Per Second (RPS)**: Jumlah requests yang berhasil diproses per detik
- **Total Requests**: Total requests selama test period

#### 3.5.3 Reliability
- **Success Rate**: Persentase requests dengan HTTP 200 OK
- **Error Rate**: Persentase requests yang gagal (HTTP 5xx)

### 3.6 Lingkungan Pengujian

**Spesifikasi Hardware**:
- Processor: Intel Core i7-10700K (8 cores, 16 threads)
- RAM: 32 GB DDR4
- Storage: NVMe SSD 1TB
- Network: Localhost (loopback interface)

**Spesifikasi Software**:
- OS: Windows 11 Professional
- Docker Desktop: v4.24
- Node.js: v18.17.0
- NGINX: v1.24.0 (Alpine)
- Artillery: v2.0.0

**Resource Allocation**:
- Docker Memory: 8 GB
- Docker CPU: 4 cores
- Per Service Memory Limit: 512 MB
- Per Service CPU Limit: 0.5 core

### 3.7 Prosedur Eksperimen

1. **Setup Phase**
   - Build Docker images untuk microservices
   - Konfigurasi NGINX untuk setiap strategi
   - Verifikasi health checks semua services

2. **Warm-up Phase**
   - Run 1 menit warm-up requests
   - Memastikan JIT compilation dan caching stabil

3. **Testing Phase**
   - Untuk setiap strategi load balancing:
     - Start containers dengan docker-compose
     - Wait 30 detik untuk service initialization
     - Run test scenario (low/medium/high)
     - Collect metrics ke JSON file
     - Cooldown 10 detik antar tests
     - Stop containers
   - Ulangi 3 kali per kondisi (N=3)

4. **Data Collection**
   - Export Artillery JSON results
   - Extract aggregate metrics
   - Backup raw data

### 3.8 Analisis Data

#### 3.8.1 Statistik Deskriptif
- Mean, standard deviation untuk setiap metrik
- Visualisasi: bar charts, line graphs, box plots

#### 3.8.2 Uji Statistik
- **ANOVA**: Untuk membandingkan multiple groups
- **T-test**: Untuk pairwise comparisons
- **Significance level**: α = 0.05

#### 3.8.3 Tools Analisis
- Python 3.10 dengan libraries: pandas, numpy, scipy
- Microsoft Excel untuk tabulasi
- Matplotlib/Seaborn untuk visualisasi

### 3.9 Validitas dan Reliabilitas

**Internal Validity**:
- Controlled environment (Docker containers)
- Randomized test order
- Multiple replications (N=3)

**External Validity**:
- Realistic workload (e-commerce pattern)
- Industry-standard tools (NGINX, Node.js)
- Reproducible setup (Docker Compose)

**Reliability**:
- Consistent test parameters
- Automated testing (mengurangi human error)
- Data backup dan verification

---

## 4. HASIL DAN PEMBAHASAN

### 4.1 Hasil Pengujian Performa Normal

Tabel 4 menyajikan hasil pengukuran response time pada seluruh kombinasi strategi dan tingkat beban. Pada beban rendah dan sedang, ketiga strategi menunjukkan performa yang hampir identik dengan perbedaan median kurang dari 2.3 ms—suatu perbedaan yang tidak signifikan secara statistik maupun praktis. Perbedaan bermakna mulai muncul pada beban tinggi, khususnya pada tail latency (P99): WRR mencatat P99 terendah (292.2 ± 13.7 ms), diikuti LC (313.1 ± 54.7 ms), dan RR tertinggi (361.0 ± 67.4 ms). Pola ini divisualisasikan pada Gambar 2 dan Gambar 3.

**Tabel 4. Response Time Comparison (ms)**

| Strategy | Load Level | Median ± SD | P95 ± SD | P99 ± SD |
|----------|------------|-------------|----------|----------|
| **Round Robin** | Low | 116.4 ± 1.3 | 194.4 ± 0.0 | 203.8 ± 2.4 |
|  | Medium | 117.9 ± 0.0 | 195.7 ± 2.3 | 205.1 ± 2.4 |
|  | High | 125.3 ± 4.3 | 252.7 ± 40.0 | 361.0 ± 67.4 |
| **Least Connection** | Low | 117.1 ± 1.3 | 194.4 ± 0.0 | 202.4 ± 0.0 |
|  | Medium | 115.6 ± 2.3 | 195.7 ± 2.3 | 205.1 ± 4.7 |
|  | High | 121.2 ± 5.7 | 227.4 ± 39.7 | 313.1 ± 54.7 |
| **Weighted RR** | Low | 117.1 ± 1.3 | 194.4 ± 0.0 | 202.4 ± 0.0 |
|  | Medium | 115.6 ± 0.0 | 194.4 ± 0.0 | 202.4 ± 0.0 |
|  | High | 120.3 ± 0.0 | 209.3 ± 4.8 | 292.2 ± 13.7 |

![Gambar 2. Perbandingan Median Response Time pada Berbagai Tingkat Beban](figures/figure1_response_time.png)

**Gambar 2.** Perbandingan median response time ketiga strategi load balancing pada tiga tingkat beban. Error bars menunjukkan standard deviation dari 3 replikasi.

WRR mencatat P99 yang 19.1% lebih rendah dibandingkan RR pada beban tinggi (292.2 ms vs 361.0 ms), sementara LC menunjukkan P99 yang 13.3% lebih rendah (313.1 ms vs 361.0 ms), sebagaimana ditunjukkan pada Gambar 3. Temuan bahwa perbedaan relatif kecil pada median namun signifikan pada P99 menunjukkan bahwa strategi load balancing terutama memengaruhi outlier requests pada ekor distribusi response time. Selain itu, standard deviation P99 pada beban tinggi menunjukkan bahwa WRR memiliki konsistensi tertinggi (SD = 13.7 ms), sementara RR paling variabel (SD = 67.4 ms)—hal ini disebabkan oleh mekanisme distribusi deterministik WRR yang menghasilkan pola routing lebih prediktabel. Tren divergensi P99 dari beban rendah ke tinggi divisualisasikan pada Gambar 4.

![Gambar 3. Perbandingan Tail Latency (P95 & P99) pada High Load](figures/figure2_tail_latency_high.png)

**Gambar 3.** Perbandingan P95 dan P99 tail latency pada high load (1000 users). Weighted RR menunjukkan P99 terendah dengan variabilitas paling kecil.

![Gambar 4. Tren P99 Latency pada Berbagai Tingkat Beban](figures/figure3_p99_trend.png)

**Gambar 4.** Tren P99 latency dari low ke high load. Round Robin menunjukkan kenaikan P99 paling tajam seiring meningkatnya beban.

Dari sisi throughput, ketiga strategi mencapai nilai identik pada seluruh tingkat beban (15.0, 39.8, dan 83.2 RPS untuk beban rendah, sedang, dan tinggi), sebagaimana disajikan pada Tabel 5 dan Gambar 5. Hal ini menunjukkan bahwa pada kapasitas server yang memadai, strategi load balancing bukan faktor pembatas throughput; diferensiasi performa tercermin pada distribusi response time, bukan pada throughput agregat.

**Tabel 5. Throughput Comparison (Requests Per Second)**

| Strategy | Load Level | Mean RPS | Total Requests | Duration (s) |
|----------|------------|----------|----------------|-------------|
| **Round Robin** | Low | 15.0 | 3,600 | 241 |
|  | Medium | 39.8 | 12,000 | 301 |
|  | High | 83.2 | 30,000 | 361 |
| **Least Connection** | Low | 15.0 | 3,600 | 241 |
|  | Medium | 39.8 | 12,000 | 301 |
|  | High | 83.2 | 30,000 | 361 |
| **Weighted RR** | Low | 15.0 | 3,600 | 241 |
|  | Medium | 39.8 | 12,000 | 301 |
|  | High | 83.2 | 30,000 | 361 |

![Gambar 5. Perbandingan Throughput pada Berbagai Tingkat Beban](figures/figure4_throughput.png)

**Gambar 5.** Perbandingan throughput ketiga strategi. Semua strategi mencapai throughput identik pada kondisi normal.

Untuk reliability, RR dan LC mencatat success rate 100% di seluruh tingkat beban, sementara WRR mengalami error rate marginal 0.0044% pada beban tinggi (rata-rata 1.3 errors dari 30.000 requests), kemungkinan disebabkan oleh service dengan weight tertinggi (weight=3) yang mengalami occasional timeout pada peak moments. Secara keseluruhan, pada kondisi normal, pemilihan strategi load balancing tidak berdampak signifikan terhadap reliability maupun throughput—perbedaan substantif baru muncul pada tail latency di beban tinggi dan, secara lebih dramatis, pada kondisi failure.

Perbandingan multidimensi performa pada beban tinggi divisualisasikan melalui radar chart pada Gambar 6, yang menampilkan lima dimensi evaluasi (response time, tail latency P99, konsistensi, throughput, dan reliability) secara simultan.

![Gambar 6. Perbandingan Performa Keseluruhan pada High Load (Radar Chart)](figures/figure5_radar.png)

**Gambar 6.** Radar chart perbandingan performa keseluruhan pada high load. Skor dinormalisasi 0-100. Ketiga strategi relatif serupa pada kondisi normal, dengan WRR sedikit unggul pada konsistensi dan tail latency.

### 4.2 Evaluasi Fault Tolerance

Untuk mengevaluasi resilience terhadap service failures—aspek yang kurang mendapat perhatian dalam literatur (Basiri et al., 2016)—dilakukan controlled failure injection dengan skenario pada Tabel 6.

**Tabel 6. Failure Test Scenarios**

| Scenario | Services Stopped | Capacity Loss | Purpose |
|----------|------------------|---------------|---------|
| Baseline | None | 0% | Reference performance |
| Single Failure | 1 out of 4 | 25% | Common failure case |
| Dual Failure | 2 out of 4 | 50% | Severe degradation |
| High-Weight Failure | Service 1 (weight=3) | ~37.5% (WRR only) | Impact of losing highest-weighted server |
| Recovery | Restart failed services | Restore capacity | Recovery behavior |

Setiap skenario dijalankan 3 kali (kecuali recovery: 1 kali) pada high load (50-100 req/s).

**Tabel 7. Response Time Under Single Service Failure (25% Capacity Loss)**

| Strategy | Baseline Median | Failure Median | Baseline P99 | Failure P99 | Baseline Mean | Failure Mean |
|----------|----------------|----------------|--------------|-------------|---------------|-------------|
| Round Robin | 120.3 ms | 120.3 ms | 284.3 ms | **894.8 ms** | 126.3 ms | **153.3 ms** |
| Least Connection | 120.3 ms | 120.3 ms | 276.9 ms | 282.4 ms | 125.7 ms | 126.0 ms |
| Weighted RR | 120.3 ms | 120.3 ms | 275.1 ms | 280.6 ms | 125.4 ms | 126.2 ms |

Pada single failure (Tabel 7), P99 Round Robin melonjak dari 284.3 ms ke 894.8 ms (+215%), sementara LC dan WRR tetap stabil dengan perubahan kurang dari 3%. Median tetap stabil pada 120.3 ms untuk semua strategi, menunjukkan bahwa dampak failure terkonsentrasi pada tail latency. Mean response time RR meningkat 21% (126.3 → 153.3 ms), sedangkan LC dan WRR tidak menunjukkan perubahan bermakna.

**Tabel 8. Response Time Under Dual Service Failure (50% Capacity Loss)**

| Strategy | Baseline Median | Failure Median | Baseline P99 | Failure P99 | Baseline Mean | Failure Mean | Errors |
|----------|----------------|----------------|--------------|-------------|---------------|-------------|--------|
| Round Robin | 120.3 ms | 121.1 ms | 284.3 ms | **2,635.7 ms** | 126.3 ms | **179.6 ms** | 6 (1 run) |
| Least Connection | 120.3 ms | 117.9 ms | 276.9 ms | 275.1 ms | 125.7 ms | 125.1 ms | 0 |
| Weighted RR | 120.3 ms | 120.3 ms | 275.1 ms | 276.9 ms | 125.4 ms | 125.5 ms | 0 |

Pada dual failure (Tabel 8), degradasi Round Robin menjadi katastrofik: P99 melonjak ke 2.635.7 ms (+827%), mean meningkat 42% (126.3 → 179.6 ms), dan terjadi 6 failed requests. LC dan WRR tetap mempertahankan P99 stabil (perubahan < 1%) dengan zero errors. Pola degradasi ini divisualisasikan pada Gambar 7 dan Gambar 8.

![Gambar 7. P99 Latency Under Failure Scenarios](figures/figure6_fault_tolerance.png)

**Gambar 7.** P99 latency pada berbagai skenario failure. Round Robin menunjukkan degradasi katastrofik pada dual failure (+827%), sementara LC dan WRR tetap stabil (< 1%).

![Gambar 8. Mean Response Time Under Failure Scenarios](figures/figure7_fault_mean_rt.png)

**Gambar 8.** Mean response time pada kondisi baseline, single failure, dan dual failure. Round Robin mengalami peningkatan 42% pada dual failure, sedangkan LC dan WRR tidak menunjukkan perubahan signifikan.

Degradasi pada Round Robin disebabkan oleh sifat static routing-nya yang tetap mengirim request ke server gagal hingga NGINX mendeteksi failure, memerlukan beberapa failed requests dan akumulasi timeout sebelum failover. LC dan WRR secara natural menghindari server gagal melalui mekanisme routing adaptif mereka—LC berdasarkan connection count, WRR melalui penghapusan server dari pool setelah health check failure.

Pengujian tambahan pada WRR menunjukkan bahwa kehilangan server dengan weight tertinggi (svc-1, weight=3, ~37.5% traffic) tidak menyebabkan degradasi lebih besar dibandingkan kehilangan server biasa (Tabel 9). P99 justru sedikit membaik (275.1 → 273.2 ms) karena distribusi traffic menjadi lebih merata di antara remaining servers. Untuk recovery behavior, semua strategi menunjukkan pemulihan cepat ke performa baseline (< 1 detik) setelah failed services di-restart, dengan success rate kembali ke 100%.

**Tabel 9. Weighted RR Under High-Weight Failure (Service 1, weight=3)**

| Metric | Baseline | Normal Failure (any) | High-Weight Failure (svc-1) |
|--------|----------|---------------------|---------------------------|
| Median | 120.3 ms | 120.3 ms | 117.9 ms |
| P99 | 275.1 ms | 280.6 ms | 273.2 ms |
| Mean | 125.4 ms | 126.2 ms | 125.2 ms |
| Success Rate | 100% | 100% | 100% |

Tabel 10 merangkum skor fault tolerance keseluruhan. Round Robin memperoleh rating **Poor** dengan P99 spike 215–827% dan terjadinya errors, sementara LC dan WRR memperoleh rating **Excellent** dengan perubahan P99 < 3% dan zero errors di seluruh skenario.

**Tabel 10. Ringkasan Fault Tolerance Score**

| Strategy | P99 Stability (1-svc) | P99 Stability (2-svc) | Error Resilience | Overall Rating |
|----------|----------------------|----------------------|------------------|----------------|
| Round Robin | ❌ +215% spike | ❌ +827% spike | ❌ Errors occurred | **Poor** |
| Least Connection | ✅ < 3% change | ✅ < 1% change | ✅ Zero errors | **Excellent** |
| Weighted RR | ✅ < 3% change | ✅ < 1% change | ✅ Zero errors | **Excellent** |

### 4.3 Pembahasan

Temuan paling signifikan dari penelitian ini adalah bahwa perbedaan performa antar strategi pada kondisi normal relatif kecil (< 5% pada median, < 20% pada P99 di beban tinggi), namun perbedaan fault tolerance sangat dramatis. Pada kondisi normal, pemilihan strategi memiliki dampak minimal—ketiga strategi mencapai throughput identik dan success rate mendekati 100%. Nilai sebenarnya dari strategi adaptif seperti LC dan WRR terungkap pada saat terjadi failures, di mana RR menunjukkan kerentanan katastrofik sedangkan LC dan WRR mempertahankan stabilitas. Oleh karena itu, proses pengambilan keputusan harus mempertimbangkan worst-case scenarios, bukan hanya normal operations.

Hasil ini konsisten dengan findings studi sebelumnya: Ghomi et al. (2017) menyatakan LC generally outperforms, yang terkonfirmasi pada tail latency di high load; Randles et al. (2010) menemukan RR sufficient untuk uniform load, yang terkonfirmasi pada beban rendah-sedang di mana perbedaan < 2%. Kontribusi novel penelitian ini adalah kuantifikasi empiris perbedaan fault tolerance yang belum diteliti sebelumnya.

Secara praktis, temuan ini memberikan kerangka keputusan bagi software architects: (1) untuk sistem dengan beban predictable tanpa risiko failure, ketiga strategi dapat diterima; (2) untuk production systems yang memerlukan fault tolerance, LC atau WRR sangat direkomendasikan; (3) untuk server heterogen, WRR optimal karena mendukung konfigurasi weight; (4) secara default, LC direkomendasikan sebagai pilihan utama karena menawarkan fault tolerance terbaik dengan kompleksitas konfigurasi rendah.

### 4.4 Limitasi

Penelitian ini memiliki beberapa limitasi. Pertama, pengujian dilakukan pada localhost environment yang tidak sepenuhnya merepresentasikan network latency pada distributed systems, meskipun relative performance antar strategi tetap valid. Kedua, microservice hanya melakukan simple CRUD operations dengan simulated processing time (50-200ms), yang tidak mencakup complex business logic. Ketiga, failure scenarios terbatas pada controlled service shutdown dan belum mencakup cascading failures, network partitions, atau Byzantine failures. Keempat, ukuran sampel N=3 per kondisi membatasi kekuatan uji statistik formal. Kelima, penelitian terbatas pada 4 service instances yang mungkin tidak merepresentasikan scalability patterns pada larger deployments. Meskipun demikian, temuan utama—khususnya perbedaan dramatis pada fault tolerance—terkonfirmasi konsisten di semua replikasi.

---

## 5. KESIMPULAN DAN SARAN

Berdasarkan hasil penelitian eksperimental yang telah dilakukan dengan total 64 experimental runs (27 performance tests + 37 failure tests), dapat disimpulkan sebagai berikut.

Pertama, pada kondisi normal (semua services healthy), ketiga strategi load balancing menunjukkan performa yang sebanding. Perbedaan median response time < 5 ms pada beban rendah-sedang, dengan throughput dan success rate yang identik (100% untuk RR dan LC, 99.9956% untuk WRR). Perbedaan mulai terlihat pada tail latency (P99) di beban tinggi, dengan Weighted Round Robin menunjukkan P99 terendah (292.2 ± 13.7 ms) dan konsistensi tertinggi, diikuti Least Connection (313.1 ± 54.7 ms) dan Round Robin (361.0 ± 67.4 ms).

Kedua, evaluasi fault tolerance mengungkapkan perbedaan paling signifikan antar strategi. Pada dual service failure (50% capacity loss), P99 Round Robin melonjak dari 284 ms ke 2.636 ms (peningkatan 827%), mean response time meningkat 42% (126 → 180 ms), dan terjadi failed requests. Sebaliknya, Least Connection dan Weighted Round Robin mempertahankan performa stabil dengan perubahan P99 kurang dari 1%, zero errors, dan mean response time yang tidak berubah signifikan.

Ketiga, temuan utama penelitian ini menunjukkan bahwa pemilihan strategi load balancing memiliki dampak terbesar bukan pada normal performance, melainkan pada fault tolerance. Ini merupakan kontribusi novel yang mengisi gap dalam literatur, di mana mayoritas studi sebelumnya hanya mengevaluasi performance pada kondisi normal.

Berdasarkan hasil penelitian, disarankan bagi praktisi untuk menggunakan Least Connection atau Weighted Round Robin sebagai default choice untuk production systems yang memerlukan high availability, mengingat resilience yang superior terhadap service failures. Round Robin dapat digunakan untuk lingkungan development/testing atau aplikasi dengan beban rendah di mana risiko failure minimal. Untuk penelitian lanjutan, disarankan evaluasi pada cloud-based deployments dengan network latency nyata, pengujian strategi advanced seperti Consistent Hashing dan Random with Two Choices, serta chaos engineering experiments yang lebih komprehensif mencakup cascading failures dan network partitions.

---

## REFERENSI

Arcuri, A., & Briand, L. (2014). A hitchhiker's guide to statistical tests for assessing randomized algorithms in software engineering. *Software Testing, Verification and Reliability*, 24(3), 219-250. https://doi.org/10.1002/stvr.1486

Balalaie, A., Heydarnoori, A., & Jamshidi, P. (2016). Microservices architecture enables DevOps: Migration to a cloud-native architecture. *IEEE Software*, 33(3), 42-52. https://doi.org/10.1109/MS.2016.64

Basiri, A., Behnam, N., de Rooij, R., Hochstein, L., Kosewski, L., Reynolds, J., & Rosenthal, C. (2016). Chaos engineering. *IEEE Software*, 33(3), 35-41. https://doi.org/10.1109/MS.2016.60

Burns, B. (2018). *Designing distributed systems: Patterns and paradigms for scalable, reliable services*. O'Reilly Media.

Di Francesco, P., Malavolta, I., & Lago, P. (2017). Research on architecting microservices: Trends, focus, and potential for industrial adoption. In *2017 IEEE International Conference on Software Architecture (ICSA)* (pp. 21-30). IEEE. https://doi.org/10.1109/ICSA.2017.24

Dragoni, N., Giallorenzo, S., Lafuente, A. L., Mazzara, M., Montesi, F., Mustafin, R., & Safina, L. (2017). Microservices: Yesterday, today, and tomorrow. In M. Mazzara & B. Meyer (Eds.), *Present and ulterior software engineering* (pp. 195-216). Springer. https://doi.org/10.1007/978-3-319-67425-4_12

Field, A. (2018). *Discovering statistics using IBM SPSS statistics* (5th ed.). SAGE Publications.

Fowler, M., & Lewis, J. (2014). Microservices: A definition of this new architectural term. Retrieved from https://martinfowler.com/articles/microservices.html

Gan, Y., Zhang, Y., Cheng, D., Shetty, A., Rathi, P., Katarki, N., Bruno, A., Hu, J., Ritber, B., Ferber, D., & Delimitrou, C. (2019). An open-source benchmark suite for microservices and their hardware-software implications for cloud & edge systems. In *Proceedings of the Twenty-Fourth International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)* (pp. 3-18). ACM. https://doi.org/10.1145/3297858.3304013

Ghomi, E. J., Rahmani, A. M., & Qader, N. N. (2017). Load-balancing algorithms in cloud computing: A survey. *Journal of Network and Computer Applications*, 88, 50-71. https://doi.org/10.1016/j.jnca.2017.04.007

Heorhiadi, V., Rajagopalan, S., Jamjoom, H., Reiter, M. K., & Sekar, V. (2016). Gremlin: Systematic resilience testing of microservices. In *2016 IEEE 36th International Conference on Distributed Computing Systems (ICDCS)* (pp. 57-66). IEEE. https://doi.org/10.1109/ICDCS.2016.11

Jamshidi, P., Pahl, C., Mendonça, N. C., Lewis, J., & Tilkov, S. (2018). Microservices: The journey so far and challenges ahead. *IEEE Software*, 35(3), 24-35. https://doi.org/10.1109/MS.2018.2141039

Kratzke, N., & Quint, P. C. (2017). Understanding cloud-native applications after 10 years of cloud computing — A systematic mapping study. *Journal of Systems and Software*, 126, 1-16. https://doi.org/10.1016/j.jss.2017.01.001

Merkel, D. (2014). Docker: Lightweight Linux containers for consistent development and deployment. *Linux Journal*, 2014(239), 2.

Newman, S. (2021). *Building microservices: Designing fine-grained systems* (2nd ed.). O'Reilly Media.

NGINX. (2024). Using nginx as HTTP load balancer. Retrieved from https://nginx.org/en/docs/http/load_balancing.html

Nygard, M. T. (2018). *Release it! Design and deploy production-ready software* (2nd ed.). Pragmatic Bookshelf.

Randles, M., Lamb, D., & Taleb-Bendiab, A. (2010). A comparative study into distributed load balancing algorithms for cloud computing. In *2010 IEEE 24th International Conference on Advanced Information Networking and Applications Workshops* (pp. 551-556). IEEE. https://doi.org/10.1109/WAINA.2010.85

Richardson, C. (2018). *Microservices patterns: With examples in Java*. Manning Publications.

Soldani, J., Tamburri, D. A., & Van Den Heuvel, W. J. (2018). The pains and gains of microservices: A systematic grey literature review. *Journal of Systems and Software*, 146, 215-232. https://doi.org/10.1016/j.jss.2018.09.082

Taibi, D., Lenarduzzi, V., & Pahl, C. (2017). Processes, motivations, and issues for migrating to microservices architectures: An empirical investigation. *IEEE Cloud Computing*, 4(5), 22-32. https://doi.org/10.1109/MCC.2017.4250931

Tanenbaum, A. S., & Van Steen, M. (2017). *Distributed systems: Principles and paradigms* (3rd ed.). CreateSpace Independent Publishing.

Thönes, J. (2015). Microservices. *IEEE Software*, 32(1), 116. https://doi.org/10.1109/MS.2015.11

Villamizar, M., Garcés, O., Castro, H., Verano, M., Salamanca, L., Casallas, R., & Gil, S. (2015). Evaluating the monolithic and the microservice architecture pattern to deploy web applications in the cloud. In *2015 10th Computing Colombian Conference (10CCC)* (pp. 583-590). IEEE. https://doi.org/10.1109/ColumbianCC.2015.7333476

---

## LAMPIRAN

### Lampiran A: Source Code

Source code lengkap tersedia di GitHub repository:
https://github.com/[username]/load-balancing-comparison

### Lampiran B: Raw Data

Complete raw data dari 64 test runs (27 performance + 37 failure) tersedia dalam format JSON:
- `data/performance_tests/` (27 files: 3 strategies × 3 loads × 3 runs)
- `data/failure_tests/` (37 files: baseline, 1-service, 2-services, recovery, high-weight)

### Lampiran C: Configuration Files

Semua konfigurasi NGINX dan Docker Compose tersedia di direktori:
- `experiment/nginx/`
- `experiment/docker-compose-*.yml`

---

**Correspondence**:
[Nama Anda]  
[Institusi]  
[Email]  
[ORCID ID]

**Conflict of Interest**: The authors declare no conflict of interest.

**Funding**: This research received no external funding.

**Data Availability**: Data and code are available at [GitHub URL].

---

*Artikel Ilmiah - Analisis Performa dan Fault Tolerance Strategi Load Balancing*  
*Draft v6.0 - April 14, 2026*  
*Tables: 10, Figures: 8*
*References: 24*

