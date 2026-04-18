# ANALISIS PERFORMA DAN RESILIENCE STRATEGI LOAD BALANCING PADA ARSITEKTUR MICROSERVICES DENGAN CONTROLLED FAILURE INJECTION

Muhammad Reza Zulman¹*, Husaini², Rahmat Hidayat³  
¹˒²˒³Jurusan Teknologi Informasi dan Komputer, Politeknik Negeri Lhokseumawe  
Jl. Medan - Banda Aceh No.Km. 280, Buketrata, Mesjid Punteut, Kec. Blang Mangat, Kota Lhokseumawe, Aceh 24301  
*Corresponding author: rezazulman@pnl.ac.id

---

## ABSTRAK

Arsitektur microservices telah menjadi paradigma dominan dalam pengembangan aplikasi modern, namun distribusi beban yang optimal dan resilience terhadap failures masih menjadi tantangan signifikan. Studi ini menganalisis performa dan fault tolerance tiga strategi load balancing (Round Robin, Least Connection, dan Weighted Round Robin) pada arsitektur microservices. Eksperimen dilakukan menggunakan sistem e-commerce berbasis Node.js dan NGINX pada tiga tingkat beban dengan tiga replikasi per kondisi. Hasil menunjukkan bahwa pada kondisi normal, ketiga strategi memberikan performa sebanding (perbedaan median < 5 ms). Perbedaan signifikan muncul pada tail latency (P99) di beban tinggi: Weighted Round Robin terendah (292.2 ± 13.7 ms), diikuti Least Connection (313.1 ± 54.7 ms) dan Round Robin (361.0 ± 67.4 ms). Pada dual service failure (50% capacity loss), P99 Round Robin melonjak 827%, sementara Least Connection dan Weighted Round Robin tetap stabil (< 1%). Least Connection dan Weighted Round Robin direkomendasikan untuk production systems yang memerlukan fault tolerance tinggi.

**Kata kunci**: load balancing, microservices, performance evaluation, container orchestration, fault tolerance

---

## ABSTRACT

Microservices architecture has become the dominant paradigm in modern application development, yet optimal load distribution and failure resilience remain significant challenges. This study analyzes the performance and fault tolerance of three load balancing strategies (Round Robin, Least Connection, and Weighted Round Robin) in microservices architecture. Experiments were conducted using a Node.js-based e-commerce system with NGINX under three load levels with three replications. Under normal conditions, all strategies showed comparable median response times (differences < 5 ms). Significant differences emerged in P99 tail latency under high load: Weighted Round Robin lowest (292.2 ± 13.7 ms), followed by Least Connection (313.1 ± 54.7 ms) and Round Robin (361.0 ± 67.4 ms). Under dual service failure (50% capacity loss), Round Robin's P99 surged 827%, while Least Connection and Weighted Round Robin remained stable (< 1% change). Least Connection and Weighted Round Robin are recommended for production systems requiring high fault tolerance.

**Keywords**: load balancing, microservices, performance evaluation, container orchestration, fault tolerance

---

## 1. PENDAHULUAN

Transformasi digital telah mendorong evolusi arsitektur perangkat lunak dari monolitik menuju microservices, yang menawarkan skalabilitas, fleksibilitas, dan kemudahan maintenance yang lebih baik (Mushtaq et al., 2022). Namun, kompleksitas distribusi beban kerja antar layanan menjadi tantangan signifikan (Weerasinghe & Perera, 2023), menjadikan load balancing komponen kritis dalam memastikan performa optimal (Selvakumar et al., 2023).

Berbagai strategi load balancing — Round Robin (RR), Least Connection (LC), dan Weighted Round Robin (WRR) — memiliki karakteristik dan trade-off yang berbeda. Literatur menunjukkan kurangnya studi eksperimental komprehensif yang membandingkan performanya dalam konteks microservices, terutama aspek fault tolerance (Lei, 2023). Penelitian sebelumnya mayoritas bersifat teoretis atau simulasi (Camilli & Russo, 2022) dan umumnya fokus pada metrik tunggal tanpa mempertimbangkan throughput, scalability, dan fault tolerance secara komprehensif (Ramu, 2023).

Berdasarkan gap tersebut, studi ini menganalisis performa dan fault tolerance ketiga strategi dalam arsitektur microservices, menjawab: (1) Bagaimana performa ketiga strategi pada berbagai tingkat beban? (2) Bagaimana resilience masing-masing terhadap service failures? (3) Strategi mana yang paling optimal untuk kondisi tertentu? Kontribusi utama berupa bukti empiris komprehensif terkait fault tolerance load balancing yang belum mendapat perhatian memadai dalam literatur. Penelitian dibatasi pada implementasi menggunakan NGINX pada platform Docker dalam lingkungan lokal.

---

## 2. TINJAUAN PUSTAKA

### 2.1 Arsitektur Microservices

Microservices mengorganisasikan aplikasi sebagai kumpulan layanan kecil, loosely coupled, dan independently deployable (Dragoni et al., 2017), dengan keuntungan scalability independen (Hassan et al., 2022), resilience terhadap partial failures (Balalaie et al., 2016), dan faster deployment (Thönes, 2015). Namun, arsitektur ini membawa kompleksitas distributed system termasuk kebutuhan sophisticated load balancing (Waseem et al., 2023; Söylemez et al., 2022).

### 2.2 Load Balancing

Load balancing mendistribusikan workload secara merata untuk memaksimalkan throughput dan meminimalkan response time (Mustofa & Ramayanti, 2020; Devi et al., 2024), diimplementasikan melalui client-side (Pimparkhede, 2021), server-side (Bhattacharya et al., 2024), atau service mesh (Patwardhan, 2019).

**Round Robin** mendistribusikan requests berurutan dengan overhead minimal, namun tidak adaptive terhadap server load (Rahimov & Aghayev, 2026; Priya & Rajendran, 2025). **Least Connection** merutekan ke server dengan koneksi aktif paling sedikit, lebih adaptive namun dengan overhead tracking lebih tinggi (Rahmika et al., 2023; Wira Harjanti et al., 2022). **Weighted Round Robin** memberikan bobot berbeda berdasarkan kapasitas server, optimal untuk server heterogen namun memerlukan konfigurasi manual (Rizqi & Dwi Nuryana, 2022; Gao & Wu, 2022).

---

## 3. METODOLOGI

### 3.1 Desain Eksperimen

Studi menggunakan desain factorial 3×3 (3 strategi × 3 load levels), direplikasi 3 kali per kondisi (Montgomery, 2017; Wohlin et al., 2012). Total: 64 runs (27 performance + 37 failure tests).

**Tabel 1. Desain Eksperimen**

| Faktor | Level |
|--------|-------|
| Strategi | Round Robin, Least Connection, Weighted RR |
| Load Level | Low (10–20 req/s), Medium (25–50 req/s), High (50–100 req/s) |
| Replikasi | 3 runs per kondisi |

Pengujian menggunakan Artillery.io dengan distribusi request: GET `/api/products` 70%, GET `/api/products/:id` 20%, GET `/api/products/category/:category` 10%.

### 3.2 Arsitektur Sistem dan Konfigurasi

Sistem e-commerce berbasis microservices (Gambar 1) terdiri dari: 4 Node.js v18/Express.js service replicas (simulated processing 50–200ms), NGINX v1.24 sebagai load balancer, dan Docker Engine v24.0 untuk orkestrasi.

![Gambar 1. Arsitektur Sistem Pengujian](figures/system-architecture.png)

**Gambar 1.** Arsitektur sistem: Artillery.io → NGINX → 4 Node.js microservice instances dalam Docker containers.

Konfigurasi NGINX (Gambar 2): RR menggunakan default rotation; LC menambahkan direktif `least_conn`; WRR menggunakan weight per server (3:2:2:1).

![Gambar 2. Konfigurasi NGINX](figures/nginx-configuration.png)

**Gambar 2.** Konfigurasi NGINX upstream block untuk ketiga strategi.

### 3.3 Metrik dan Lingkungan

Metrik evaluasi: response time (median, P95, P99), throughput (RPS), dan reliability (success/error rate). Lingkungan: Intel Core i7-10700K, RAM 32 GB, NVMe SSD, Docker Desktop v4.24 (8 GB memori, 4 cores; limit per service: 512 MB, 0.5 core). Validitas dijaga melalui lingkungan terkontrol Docker, pengacakan urutan, dan replikasi 3× per kondisi.

---

## 4. HASIL DAN PEMBAHASAN

### 4.1 Performa Normal

Tabel 2 menyajikan response time pada seluruh kombinasi strategi dan beban. Pada beban rendah–sedang, perbedaan median antar strategi kurang dari 2.3 ms — tidak signifikan secara praktis. Perbedaan bermakna muncul pada P99 di beban tinggi: WRR terendah (292.2 ± 13.7 ms), LC (313.1 ± 54.7 ms), dan RR tertinggi (361.0 ± 67.4 ms), sebagaimana ditunjukkan Gambar 3–5.

**Tabel 2. Perbandingan Response Time (ms)**

| Strategi | Load | Median ± SD | P95 ± SD | P99 ± SD |
|----------|------|-------------|----------|----------|
| **Round Robin** | Low | 116.4 ± 1.3 | 194.4 ± 0.0 | 203.8 ± 2.4 |
| | Medium | 117.9 ± 0.0 | 195.7 ± 2.3 | 205.1 ± 2.4 |
| | High | 125.3 ± 4.3 | 252.7 ± 40.0 | 361.0 ± 67.4 |
| **Least Conn** | Low | 117.1 ± 1.3 | 194.4 ± 0.0 | 202.4 ± 0.0 |
| | Medium | 115.6 ± 2.3 | 195.7 ± 2.3 | 205.1 ± 4.7 |
| | High | 121.2 ± 5.7 | 227.4 ± 39.7 | 313.1 ± 54.7 |
| **Weighted RR** | Low | 117.1 ± 1.3 | 194.4 ± 0.0 | 202.4 ± 0.0 |
| | Medium | 115.6 ± 0.0 | 194.4 ± 0.0 | 202.4 ± 0.0 |
| | High | 120.3 ± 0.0 | 209.3 ± 4.8 | 292.2 ± 13.7 |

![Gambar 3. Median Response Time](figures/figure1_response_time.png)

**Gambar 3.** Perbandingan median response time. Error bars: SD dari 3 replikasi.

WRR mencatat P99 yang 19.1% lebih rendah dari RR (292.2 vs 361.0 ms), dengan konsistensi tertinggi (SD = 13.7 ms vs RR: 67.4 ms) akibat distribusi deterministik berbasis weight (Gambar 4–5).

![Gambar 4. Tail Latency High Load](figures/figure2_tail_latency_high.png)

**Gambar 4.** P95 dan P99 tail latency pada high load (1000 users).

![Gambar 5. Tren P99](figures/figure3_p99_trend.png)

**Gambar 5.** Tren P99 dari low ke high load.

Throughput identik pada seluruh strategi dan beban (15.0, 39.8, 83.2 RPS), menunjukkan strategi bukan faktor pembatas throughput (Tabel 3, Gambar 6). RR dan LC mencatat success rate 100%; WRR mengalami error marginal 0.0044% pada beban tinggi. Perbandingan multidimensi ditunjukkan pada Gambar 7.

**Tabel 3. Throughput (RPS)**

| Strategi | Low | Medium | High |
|----------|-----|--------|------|
| Round Robin | 15.0 | 39.8 | 83.2 |
| Least Connection | 15.0 | 39.8 | 83.2 |
| Weighted RR | 15.0 | 39.8 | 83.2 |

![Gambar 6. Throughput](figures/figure4_throughput.png)

**Gambar 6.** Perbandingan throughput ketiga strategi.

![Gambar 7. Radar Chart](figures/figure5_radar.png)

**Gambar 7.** Radar chart performa pada high load (skor 0–100).

### 4.2 Fault Tolerance

Controlled failure injection dilakukan dengan skenario pada Tabel 4, masing-masing 3 kali (kecuali recovery: 1 kali) pada high load.

**Tabel 4. Skenario Failure Test**

| Skenario | Services Stopped | Capacity Loss |
|----------|------------------|---------------|
| Baseline | 0 | 0% |
| Single Failure | 1 dari 4 | 25% |
| Dual Failure | 2 dari 4 | 50% |
| High-Weight Failure | Svc-1 (weight=3) | ~37.5% (WRR) |
| Recovery | Restart | Restore |

Pada single failure (Tabel 5), P99 RR melonjak dari 284.3 ke 894.8 ms (+215%), sementara LC dan WRR tetap stabil (< 3%). Pada dual failure (Tabel 6), degradasi RR menjadi katastrofik: P99 ke 2.635,7 ms (+827%), mean +42%, dan 6 failed requests. LC dan WRR mempertahankan P99 stabil (< 1%) dengan zero errors (Gambar 8–9).

**Tabel 5. Single Service Failure (25% Capacity Loss)**

| Strategi | Baseline P99 | Failure P99 | Baseline Mean | Failure Mean |
|----------|--------------|-------------|---------------|-------------|
| Round Robin | 284.3 ms | **894.8 ms** | 126.3 ms | **153.3 ms** |
| Least Conn | 276.9 ms | 282.4 ms | 125.7 ms | 126.0 ms |
| Weighted RR | 275.1 ms | 280.6 ms | 125.4 ms | 126.2 ms |

**Tabel 6. Dual Service Failure (50% Capacity Loss)**

| Strategi | Baseline P99 | Failure P99 | Failure Mean | Errors |
|----------|--------------|-------------|-------------|--------|
| Round Robin | 284.3 ms | **2.635,7 ms** | **179.6 ms** | 6 |
| Least Conn | 276.9 ms | 275.1 ms | 125.1 ms | 0 |
| Weighted RR | 275.1 ms | 276.9 ms | 125.5 ms | 0 |

![Gambar 8. Fault Tolerance P99](figures/figure6_fault_tolerance.png)

**Gambar 8.** P99 latency pada skenario failure.

![Gambar 9. Mean RT pada Failure](figures/figure7_fault_mean_rt.png)

**Gambar 9.** Mean response time pada baseline, single, dan dual failure.

Degradasi RR disebabkan static routing yang tetap mengirim request ke server gagal hingga timeout, sedangkan LC dan WRR secara natural menghindari server gagal melalui mekanisme adaptif. Pengujian tambahan WRR menunjukkan kehilangan server weight tertinggi (svc-1, ~37.5% traffic) tidak menyebabkan degradasi lebih besar — P99 justru membaik (275.1 → 273.2 ms) karena distribusi lebih merata. Semua strategi recovery cepat ke baseline (< 1 detik).

### 4.3 Pembahasan

Temuan utama: perbedaan performa pada kondisi normal relatif kecil (< 5% median, < 20% P99), namun perbedaan fault tolerance sangat dramatis. Nilai strategi adaptif (LC, WRR) terungkap saat failures — RR menunjukkan kerentanan katastrofik. Implikasi praktis: (1) untuk sistem stabil tanpa risiko failure, ketiga strategi dapat diterima; (2) untuk production systems, LC atau WRR sangat direkomendasikan; (3) untuk server heterogen, WRR optimal; (4) LC direkomendasikan sebagai default karena fault tolerance terbaik dengan konfigurasi sederhana.

### 4.4 Keterbatasan

Pengujian pada localhost tidak merepresentasikan network latency distributed systems. Microservice hanya melakukan operasi sederhana. Failure scenarios terbatas pada controlled shutdown. Ukuran sampel N=3 membatasi uji statistik formal. Meskipun demikian, temuan fault tolerance terkonfirmasi konsisten di semua replikasi.

---

## 5. KESIMPULAN DAN SARAN

Berdasarkan 64 experimental runs, diperoleh kesimpulan: (1) pada kondisi normal, ketiga strategi menunjukkan performa sebanding (median < 5 ms, throughput identik), dengan perbedaan pada P99 beban tinggi — WRR terendah (292.2 ± 13.7 ms), RR tertinggi (361.0 ± 67.4 ms); (2) fault tolerance mengungkapkan perbedaan paling signifikan — pada dual failure, P99 RR melonjak 827% dengan errors, sementara LC dan WRR stabil (< 1%, zero errors); (3) pemilihan strategi berdampak terbesar pada fault tolerance, bukan normal performance.

Disarankan menggunakan LC atau WRR untuk production systems yang memerlukan high availability. RR dapat digunakan untuk lingkungan development/testing. Penelitian lanjutan disarankan pada cloud-based deployments, strategi advanced (Consistent Hashing, Random with Two Choices), dan chaos engineering experiments yang lebih komprehensif.

---

## DAFTAR PUSTAKA

Balalaie, A., Heydarnoori, A., & Jamshidi, P. (2016). Microservices Architecture Enables DevOps: Migration to a Cloud-Native Architecture. *IEEE Software*, 33(3), 42–52. https://doi.org/10.1109/MS.2016.64

Bhattacharya, R., Gao, Y., & Wood, T. (2024). Dynamically Balancing Load with Overload Control for Microservices. *ACM Transactions on Autonomous and Adaptive Systems*, 19(4), 1–23. https://doi.org/10.1145/3676167

Camilli, M., & Russo, B. (2022). Modeling Performance of Microservices Systems with Growth Theory. *Empirical Software Engineering*, 27(2), 39. https://doi.org/10.1007/s10664-021-10088-0

Devi, N., Dalal, S., Solanki, K., Dalal, S., Lilhore, U. K., Simaiya, S., & Nuristani, N. (2024). A systematic literature review for load balancing and task scheduling techniques in cloud computing. *Artificial Intelligence Review*, 57(10), 276. https://doi.org/10.1007/s10462-024-10925-w

Dragoni, N., Giallorenzo, S., Lafuente, A. L., Mazzara, M., Montesi, F., Mustafin, R., & Safina, L. (2017). Microservices: Yesterday, Today, and Tomorrow. In M. Mazzara & B. Meyer (Eds.), *Present and Ulterior Software Engineering* (pp. 195–216). Springer. https://doi.org/10.1007/978-3-319-67425-4_12

Gao, C., & Wu, H. (2022). An Improved Dynamic Smooth Weighted Round-robin Load-balancing Algorithm. *Journal of Physics: Conference Series*, 2404(1), 012047. https://doi.org/10.1088/1742-6596/2404/1/012047

Hassan, S., Bahsoon, R., & Buyya, R. (2022). Systematic scalability analysis for microservices granularity adaptation design decisions. *Software: Practice and Experience*, 52(6), 1378–1401. https://doi.org/10.1002/spe.3069

Lei, C. (2023). A novel fault tolerance based load balancing technique in cloud computing. *Journal of Intelligent & Fuzzy Systems*, 45(2), 2931–2948. https://doi.org/10.3233/JIFS-230102

Montgomery, D. C. (2017). *Design and analysis of experiments* (9th ed.). John Wiley & Sons.

Mushtaq, Z., Saher, N., Shazad, F., Iqbal, S., & Qasim, A. (2022). A Review on Transformation of Monolithic Applications towards Microservices Environment. *International Journal of Innovations in Science and Technology*, 4(1), 1–18. https://doi.org/10.33411/IJIST/2022040101

Mustofa, A., & Ramayanti, D. (2020). Implementasi Load Balancing dan Failover to Device Mikrotik Router Menggunakan Metode NTH. *Jurnal Teknologi Informasi Dan Ilmu Komputer*, 7(1), 139–144. https://doi.org/10.25126/jtiik.2020701638

Patwardhan, K. M. (2019). Making Sense of a Service-Oriented Architecture (SOA) Governance Framework. *2019 IEEE 12th SOCA*, 49–54. https://doi.org/10.1109/SOCA.2019.00015

Pimparkhede, K. (2021). Client side and Server Side Load Balancing. *International Journal for Research in Applied Science and Engineering Technology*, 9(11), 30–31. https://doi.org/10.22214/ijraset.2021.38748

Priya, S. S., & Rajendran, T. (2025). Enhanced Weighted Round Robin: A New Paradigm in Cloud Load Balancing. *Indian Journal of Science and Technology*, 18(15), 1220–1228. https://doi.org/10.17485/IJST/v18i15.3976

Rahimov, E., & Aghayev, T. (2026). Predictive Load Balancing in Distributed Systems. *CIEES 2025*, 26. https://doi.org/10.3390/engproc2026122026

Rahmika, A. R., Tahir, Z., Paundu, A. W., & Zainuddin, Z. (2023). Web Server Load Balancing Mechanism with Least Connection Algorithm and Multi-Agent System. *CommIT Journal*, 17(2), 245–258. https://doi.org/10.21512/commit.v17i2.8872

Ramu, V. B. (2023). Performance Impact of Microservices Architecture. *The Review of Contemporary Scientific and Academic Studies*, 3(6). https://doi.org/10.55454/rcsas.3.06.2023.010

Rizqi, M. N. A., & Dwi Nuryana, I. K. (2022). Analisis Perbandingan Kinerja Algoritma Weighted Round Robin dan Weighted Least Connection. *JINACS*, 4(01), 67–75. https://doi.org/10.26740/jinacs.v4n01.p67-75

Selvakumar, G., Jayashree, L., & Arumugam, S. (2023). Latency Minimization Using an Adaptive Load Balancing Technique in Microservices. *Computer Systems Science and Engineering*, 46(1), 1215–1231. https://doi.org/10.32604/csse.2023.032509

Söylemez, M., Tekinerdogan, B., & Kolukısa Tarhan, A. (2022). Challenges and Solution Directions of Microservice Architectures. *Applied Sciences*, 12(11), 5507. https://doi.org/10.3390/app12115507

Thönes, J. (2015). Microservices. *IEEE Software*, 32(1), 116. https://doi.org/10.1109/MS.2015.11

Waseem, M., Liang, P., Ahmad, A., et al. (2023). Understanding the Issues, Their Causes and Solutions in Microservices Systems. *arXiv*. https://doi.org/10.48550/ARXIV.2302.01894

Weerasinghe, S., & Perera, I. (2023). Optimized Strategy for Inter-Service Communication in Microservices. *IJACSA*, 14(2). https://doi.org/10.14569/IJACSA.2023.0140233

Wira Harjanti, T., Setiyani, H., & Trianto, J. (2022). Load Balancing Analysis Using Round-Robin and Least-Connection Algorithms. *Applied Technology and Computing Science Journal*, 5(2), 40–49. https://doi.org/10.33086/atcsj.v5i2.3743

Wohlin, C., Runeson, P., Höst, M., Ohlsson, M. C., Regnell, B., & Wesslén, A. (2012). *Experimentation in Software Engineering*. Springer. https://doi.org/10.1007/978-3-642-29044-2

