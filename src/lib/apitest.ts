import { healthCheck } from "./api";

async function testHealthCheck() {
  try {
    const result = await healthCheck();
    console.log('✓ Health check passed:', result);
  } catch (error) {
    console.error('✗ Health check failed:', error);
  }
}

testHealthCheck();