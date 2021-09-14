#include<xc.h>           // processor SFR definitions
#include<sys/attribs.h>  // __ISR macro
#include "i2c.h"

// DEVCFG0
#pragma config DEBUG = OFF // disable debugging
#pragma config JTAGEN = OFF // disable jtag
#pragma config ICESEL = ICS_PGx1 // use PGED1 and PGEC1
#pragma config PWP = OFF // disable flash write protect
#pragma config BWP = OFF // disable boot write protect
#pragma config CP = OFF // disable code protect

// DEVCFG1
#pragma config FNOSC = FRCPLL // use primary oscillator with pll
#pragma config FSOSCEN = OFF // disable secondary oscillator
#pragma config IESO = OFF // disable switching clocks
#pragma config POSCMOD = OFF // high speed crystal mode
#pragma config OSCIOFNC = OFF // disable clock output
#pragma config FPBDIV = DIV_1 // divide sysclk freq by 1 for peripheral bus clock
#pragma config FCKSM = CSDCMD // disable clock switch and FSCM
#pragma config WDTPS = PS1048576 // use largest wdt
#pragma config WINDIS = OFF // use non-window mode wdt
#pragma config FWDTEN = OFF // wdt disabled
#pragma config FWDTWINSZ = WINSZ_25 // wdt window at 25%

// DEVCFG2 - get the sysclk clock to 48MHz from the 8MHz crystal
#pragma config FPLLIDIV = DIV_2 // divide input clock to be in range 4-5MHz
#pragma config FPLLMUL = MUL_24 // multiply clock after FPLLIDIV
#pragma config FPLLODIV = DIV_2 // divide clock after FPLLMUL to get 48MHz

// DEVCFG3
#pragma config USERID = 0 // some 16bit userid, doesn't matter what
#pragma config PMDL1WAY = OFF // allow multiple reconfigurations
#pragma config IOL1WAY = OFF // allow multiple reconfigurations


#define CLK_RATE 48000000
#define BAUD_RATE 115200

#define MCP23017_ADDR 0b0100000
#define MCP23017_IODIRA 0x00
#define MCP23017_IODIRB 0x01
#define MCP23017_GPIOA 0x12
#define MCP23017_GPIOB 0x13
#define MCP23017_OLATA 0x14
#define MCP23017_OLATB 0x15


void delay_us(int duration);
void readUART1(char * string, int maxLength);
void writeUART1(const char * string);

void write_i2c(unsigned char slave_addr, unsigned char reg_addr, unsigned char data);
unsigned char read_i2c(unsigned char slave_addr, unsigned char reg_addr);
int main() {

    __builtin_disable_interrupts(); // disable interrupts while initializing things

    // set the CP0 CONFIG register to indicate that kseg0 is cacheable (0x3)
    __builtin_mtc0(_CP0_CONFIG, _CP0_CONFIG_SELECT, 0xa4210583);

    // 0 data RAM access wait states
    BMXCONbits.BMXWSDRM = 0x0;

    // enable multi vector interrupts
    INTCONbits.MVEC = 0x1;

    // disable JTAG to get pins back
    DDPCONbits.JTAGEN = 0;

    // do your TRIS and LAT commands here
    TRISBbits.TRISB4 = 1;
    TRISAbits.TRISA4 = 0;
    LATAbits.LATA4 = 0;
    
    // UART config
    U1RXRbits.U1RXR = 0b0001; //U1RX is B6
    RPB7Rbits.RPB7R = 0b0001; //U1TX is B7
    
    // turn on UART3 without an interrupt
    U1MODEbits.BRGH = 0; // set baud to NU32_DESIRED_BAUD
    U1BRG = ((CLK_RATE / BAUD_RATE) / 16) - 1;

    // 8 bit, no parity bit, and 1 stop bit (8N1 setup)
    U1MODEbits.PDSEL = 0;
    U1MODEbits.STSEL = 0;

    // configure TX & RX pins as output & input pins
    U1STAbits.UTXEN = 1;
    U1STAbits.URXEN = 1;

    // enable the uart
    U1MODEbits.ON = 1;
    
    i2c_master_setup();
    //write_i2c(MCP23017_ADDR, MCP23017_IODIRA, 0x00); //set GPIOA to output
    //write_i2c(MCP23017_ADDR, MCP23017_IODIRB, 0xFF); //set GPIOB to input

    __builtin_enable_interrupts();
    
    char msg[100];
    unsigned char button_value;
    write_i2c(MCP23017_ADDR, MCP23017_IODIRA, 0x00); //set GPIOA to output
    write_i2c(MCP23017_ADDR, MCP23017_IODIRB, 0xFF); //set GPIOB to input
    while (1) {
        // use _CP0_SET_COUNT(0) and _CP0_GET_COUNT() to test the PIC timing
        // remember the core timer runs at half the sysclk
        _CP0_SET_COUNT(0);
        
        
        
        write_i2c(MCP23017_ADDR, MCP23017_OLATA, 0x00);
        button_value = read_i2c(MCP23017_ADDR, MCP23017_GPIOB);
        if ((button_value & 0x01) != 0x1) {
            write_i2c(MCP23017_ADDR, MCP23017_OLATA, 0x80);
        }
        
        // heartbeat
        delay_us(200000);
        LATAbits.LATA4 ^= 1;
        
    }
}


void delay_us(int duration) {
    // duration is in uS
    // math to determine ticks/uS:
    // CP0 ticks at 1/2 sysclk
    int TR = CLK_RATE/2;
    int TS = TR/1000000;
    int delay_limit = TS*duration;
    _CP0_SET_COUNT(0);
    while (1) {
        if (_CP0_GET_COUNT() >= delay_limit) {
            break;
        }
    }
    return;
}

// Read from UART3
// block other functions until you get a '\r' or '\n'
// send the pointer to your char array and the number of elements in the array
void readUART1(char * message, int maxLength) {
  char data = 0;
  int complete = 0, num_bytes = 0;
  // loop until you get a '\r' or '\n'
  while (!complete) {
    if (U1STAbits.URXDA) { // if data is available
      data = U1RXREG;      // read the data
      if ((data == '\n') || (data == '\r')) {
        complete = 1;
      } else {
        message[num_bytes] = data;
        ++num_bytes;
        // roll over if the array is too small
        if (num_bytes >= maxLength) {
          num_bytes = 0;
        }
      }
    }
  }
  // end the string
  message[num_bytes] = '\0';
}

// Write a character array using UART3
void writeUART1(const char * string) {
  while (*string != '\0') {
    while (U1STAbits.UTXBF) {
      ; // wait until tx buffer isn't full
    }
    U1TXREG = *string;
    ++string;
  }
}

void write_i2c(unsigned char slave_addr, unsigned char reg_addr, unsigned char data) {
    i2c_master_start();
    i2c_master_send(0b01000000 | (slave_addr << 1));
    i2c_master_send(reg_addr);
    i2c_master_send(data);
    i2c_master_stop();
}

unsigned char read_i2c(unsigned char slave_addr, unsigned char reg_addr) {
    unsigned char slave_byte;
    i2c_master_start();
    i2c_master_send(0b01000000 | (slave_addr << 1));
    i2c_master_send(reg_addr);
    i2c_master_restart();
    i2c_master_send(0b01000001 | (slave_addr << 1));
    slave_byte = i2c_master_recv();
    i2c_master_ack(1);
    i2c_master_stop();
    return slave_byte;
}