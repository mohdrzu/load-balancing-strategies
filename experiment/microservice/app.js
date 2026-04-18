/**
 * Simple Microservice for Load Balancing Experiment
 * Simulates a product catalog service in e-commerce system
 */

const express = require('express');
const app = express();

// Get service configuration from environment variables
const PORT = process.env.PORT || 3000;
const SERVICE_ID = process.env.SERVICE_ID || 'service-1';
const SERVICE_NAME = process.env.SERVICE_NAME || 'Product Service';

// Simulated product database
const products = [
    { id: 1, name: 'Laptop', price: 999.99, category: 'Electronics' },
    { id: 2, name: 'Mouse', price: 29.99, category: 'Electronics' },
    { id: 3, name: 'Keyboard', price: 79.99, category: 'Electronics' },
    { id: 4, name: 'Monitor', price: 299.99, category: 'Electronics' },
    { id: 5, name: 'Headphones', price: 149.99, category: 'Electronics' }
];

// Middleware to log requests
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${SERVICE_ID} - ${req.method} ${req.path}`);
    next();
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        serviceId: SERVICE_ID,
        serviceName: SERVICE_NAME,
        timestamp: new Date().toISOString()
    });
});

// Main API endpoint - Get all products
app.get('/api/products', async (req, res) => {
    const startTime = Date.now();
    
    // Simulate processing time (50-200ms random delay)
    const processingTime = Math.floor(Math.random() * 150) + 50;
    await new Promise(resolve => setTimeout(resolve, processingTime));
    
    const responseTime = Date.now() - startTime;
    
    res.json({
        serviceId: SERVICE_ID,
        serviceName: SERVICE_NAME,
        timestamp: new Date().toISOString(),
        processingTime: `${responseTime}ms`,
        totalProducts: products.length,
        data: products
    });
});

// Get product by ID
app.get('/api/products/:id', async (req, res) => {
    const startTime = Date.now();
    const productId = parseInt(req.params.id);
    
    // Simulate processing time
    const processingTime = Math.floor(Math.random() * 100) + 30;
    await new Promise(resolve => setTimeout(resolve, processingTime));
    
    const product = products.find(p => p.id === productId);
    const responseTime = Date.now() - startTime;
    
    if (product) {
        res.json({
            serviceId: SERVICE_ID,
            serviceName: SERVICE_NAME,
            timestamp: new Date().toISOString(),
            processingTime: `${responseTime}ms`,
            data: product
        });
    } else {
        res.status(404).json({
            serviceId: SERVICE_ID,
            error: 'Product not found',
            processingTime: `${responseTime}ms`
        });
    }
});

// Get products by category
app.get('/api/products/category/:category', async (req, res) => {
    const startTime = Date.now();
    const category = req.params.category;
    
    // Simulate processing time
    const processingTime = Math.floor(Math.random() * 120) + 40;
    await new Promise(resolve => setTimeout(resolve, processingTime));
    
    const filteredProducts = products.filter(p => 
        p.category.toLowerCase() === category.toLowerCase()
    );
    const responseTime = Date.now() - startTime;
    
    res.json({
        serviceId: SERVICE_ID,
        serviceName: SERVICE_NAME,
        timestamp: new Date().toISOString(),
        processingTime: `${responseTime}ms`,
        category: category,
        totalProducts: filteredProducts.length,
        data: filteredProducts
    });
});

// Simulate high CPU load endpoint (for testing resource utilization)
app.get('/api/heavy', async (req, res) => {
    const startTime = Date.now();
    
    // Simulate CPU-intensive operation
    let result = 0;
    for (let i = 0; i < 1000000; i++) {
        result += Math.sqrt(i);
    }
    
    const responseTime = Date.now() - startTime;
    
    res.json({
        serviceId: SERVICE_ID,
        serviceName: SERVICE_NAME,
        timestamp: new Date().toISOString(),
        processingTime: `${responseTime}ms`,
        message: 'Heavy computation completed',
        result: result
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        serviceId: SERVICE_ID,
        serviceName: SERVICE_NAME,
        version: '1.0.0',
        status: 'running',
        endpoints: [
            'GET /health - Health check',
            'GET /api/products - Get all products',
            'GET /api/products/:id - Get product by ID',
            'GET /api/products/category/:category - Get products by category',
            'GET /api/heavy - CPU-intensive endpoint'
        ]
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(`[${SERVICE_ID}] Error:`, err);
    res.status(500).json({
        serviceId: SERVICE_ID,
        error: 'Internal server error',
        message: err.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log(`${SERVICE_NAME} (${SERVICE_ID}) started`);
    console.log(`Port: ${PORT}`);
    console.log(`Time: ${new Date().toISOString()}`);
    console.log('='.repeat(60));
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log(`[${SERVICE_ID}] SIGTERM received. Shutting down gracefully...`);
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log(`[${SERVICE_ID}] SIGINT received. Shutting down gracefully...`);
    process.exit(0);
});

