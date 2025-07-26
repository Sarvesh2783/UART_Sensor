// ═══════════════════════════════════════════════════════════
// CONFIGURATION & CONSTANTS
// ═══════════════════════════════════════════════════════════
const unsigned long TRANSMISSION_INTERVAL = 5000;
const int BUFFER_SIZE = 64;
const float BASE_TEMP = 22.0;

// ═══════════════════════════════════════════════════════════
// STATIC MEMORY MANAGEMENT
// ═══════════════════════════════════════════════════════════
static char transmitBuffer[BUFFER_SIZE];    // Main data buffer
static char sensorID[16] = "TEMP_01";      // Sensor identifier

// ═══════════════════════════════════════════════════════════
// GLOBAL STATE VARIABLES
// ═══════════════════════════════════════════════════════════
unsigned long lastTransmissionTime = 0;
unsigned long systemStartTime = 0;
float currentTemp = BASE_TEMP;
uint16_t sequenceNumber = 0;

// ═══════════════════════════════════════════════════════════
// CORE FUNCTIONS
// ═══════════════════════════════════════════════════════════

void setup() {
    // System initialization
    initializeSystem();
}

void loop() {
    // Main execution loop
    // - Check transmission timing
    // - Generate temperature reading
    // - Format and transmit data
}

// ───────────────────────────────────────────────────────────
// INITIALIZATION FUNCTIONS
// ───────────────────────────────────────────────────────────
void initializeSystem() {
    // UART setup, buffer clearing, random seed
}

// ───────────────────────────────────────────────────────────
// SENSOR SIMULATION FUNCTIONS
// ───────────────────────────────────────────────────────────
float simulateTemperatureReading() {
    // Multi-component temperature generation:
    // - Slow variation (daily cycle simulation)
    // - Fast variation (minor fluctuations)  
    // - Random noise component
}

// ───────────────────────────────────────────────────────────
// COMMUNICATION FUNCTIONS
// ───────────────────────────────────────────────────────────
void formatUARTPacket(float temperature, unsigned long timestamp) {
    // Protocol: START|SENSOR_ID|SEQ|TIMESTAMP|TEMP|CHECKSUM|END
}

void transmitViaUART() {
    // Send formatted packet via Serial
}

uint8_t calculateChecksum(const char* data, int length) {
    // XOR checksum for data integrity
}

// ───────────────────────────────────────────────────────────
// COMMAND PROCESSING
// ───────────────────────────────────────────────────────────
void serialEvent() {
    // Handle incoming commands (R=Reset, S=Status)
}