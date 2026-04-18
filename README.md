## Research Project: Load Balancing Strategies in Microservices Architecture

---

## Quick Start - Run Experiments

### Prerequisites

#### Required:
- Docker Desktop (running)
- Node.js & npm
- Artillery (`npm install -g artillery`)
- Python 3.x (for analysis)
- Git Bash (for Windows)

#### Verify Setup:
```bash
bash tests/run-check-test.sh
```

### Running Tests

#### 1. Performance Tests
```bash
bash tests/run-performance-tests.sh
```
- Tests 3 strategies × 3 load levels × 3 runs = **27 tests**
- Results saved in `result-data/performance_tests/`

#### 2. Failure/Fault Tolerance Tests
```bash
bash tests/test-failure-scenarios.sh
```
- Tests multiple failure scenarios (baseline, 1-service down, 2-services down, recovery)
- Results saved in `result-data/failure_tests/`

---

## Research Scope

**Research Questions**:
1. How do different load balancing strategies perform under various load conditions?
2. How do strategies handle service failures (fault tolerance)?
3. Which strategy provides the best trade-off between performance and resilience?

**Strategies Compared**:
1. **Round Robin** - Sequential distribution
2. **Least Connection** - Dynamic load-based
3. **Weighted** - Priority-based distribution

**Evaluation Metrics**:
- Response Time (ms)
- Throughput (req/s)
- Success Rate (%)
- Error Rate (%)
- Recovery Time (fault tolerance)
- Resource Utilization

**Experimental Setup**:
- 3 microservice instances
- NGINX load balancer
- Artillery load testing tool
- Docker containerization
- 3 load levels (Low, Medium, High)
- 3 runs per scenario for statistical validation
- Failure injection scenarios

---

## Project Structure

```
load-balancing-comparison/
├── experiment/          # Docker Compose & microservice configs
│   ├── docker-compose-rr.yml
│   ├── docker-compose-lc.yml
│   ├── docker-compose-weighted.yml
│   ├── microservice/    # Node.js microservice source
│   └── nginx/           # NGINX load balancer configs
├── result-data/
│   ├── performance_tests/   # 27 JSON result files (3 strategies × 3 loads × 3 runs)
│   └── failure_tests/       # 33 JSON result files (fault tolerance scenarios)
├── scripts/             # Python analysis & figure generation scripts
├── tests/               # Shell scripts & Artillery test configs
├── figures/             # Generated charts and diagrams
└── publication/         # Article drafts (MD & DOCX)
```

---

## Expected Output

After running all tests:
- **27** performance test files in `result-data/performance_tests/`
- **33** fault tolerance test files in `result-data/failure_tests/`
- **Total: 60 test result files**
