#include<xc.h>           // processor SFR definitions
#include<sys/attribs.h>  // __ISR macro

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


void delay_us(int duration);
unsigned char spi_io(unsigned char o);
void initSPI();

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

    
    // SPI config
    unsigned short TRIANGLE_WAVE[100] = {0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000, 980, 960, 940, 920, 900, 880, 860, 840, 820, 800, 780, 760, 740, 720, 700, 680, 660, 640, 620, 600, 580, 560, 540, 520, 500, 480, 460, 440, 420, 400, 380, 360, 340, 320, 300, 280, 260, 240, 220, 200, 180, 160, 140, 120, 100, 80, 60, 40, 20};
    unsigned short SINE_WAVE[100] = {500, 531, 562, 593, 624, 654, 684, 712, 740, 767, 793, 818, 842, 864, 885, 904, 922, 938, 952, 964, 975, 984, 991, 996, 999, 1000, 999, 996, 991, 984, 975, 964, 952, 938, 922, 904, 885, 864, 842, 818, 793, 767, 740, 712, 684, 654, 624, 593, 562, 531, 499, 468, 437, 406, 375, 345, 315, 287, 259, 232, 206, 181, 157, 135, 114, 95, 77, 61, 47, 35, 24, 15, 8, 3, 0, 0, 0, 3, 8, 15, 24, 35, 47, 61, 77, 95, 114, 135, 157, 181, 206, 232, 259, 287, 315, 345, 375, 406, 437, 468};

    initSPI();
    unsigned short voltage;
    unsigned char channel;
    unsigned short p;
    

    __builtin_enable_interrupts();

    int iterator = 0;
    while (1) {
        
        
        // use _CP0_SET_COUNT(0) and _CP0_GET_COUNT() to test the PIC timing
        // remember the core timer runs at half the sysclk
        //_CP0_SET_COUNT(0);
        
        //TODO: WRITE LOOP TO SEND ELEMENTS FROM TRIANGLE_WAVE AND SINE_WAVE TO SLAVE, DELAY BY 10000 uS
       
        channel = 0;
        voltage = SINE_WAVE[iterator];
        p = channel<<15|(0b111<<12);
        p = p|(voltage<<2);
        
     
        LATBbits.LATB15 = 0;
        spi_io(p>>8);
        spi_io(p);
        LATBbits.LATB15 = 1;
        
        
        channel = 1;
        voltage = TRIANGLE_WAVE[iterator];
        p = (channel<<15)|(0b111<<12);
        p = p|(voltage<<2);
        
        
        LATBbits.LATB15 = 0;
        spi_io(p>>8);
        spi_io(p);
        
        LATBbits.LATB15 = 1;
        iterator++;
        if (iterator == 100) {
            iterator = 0;
        }
        
        
        delay_us(10000);
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

// initialize SPI1
void initSPI() {
    // Pin B14 has to be SCK1
    // Turn of analog pins
    //...
    // Make an output pin for CS
    //...
    //...
    // Set SDO1
    //...
    // Set SDI1
    //...

    ANSELB = 0;
    TRISBbits.TRISB15 = 0; // CS is B15
    LATBbits.LATB15 = 1;
    RPB11Rbits.RPB11R = 0b0011; //SDO1 is B11
    SDI1Rbits.SDI1R = 0b0100; //SDI1 is B8
    
    // setup SPI1
    SPI1CON = 0; // turn off the spi module and reset it
    SPI1BUF; // clear the rx buffer by reading from it
    SPI1BRG = 1000; // 1000 for 24kHz, 1 for 12MHz; // baud rate to 10 MHz [SPI1BRG = (48000000/(2*desired))-1]
    SPI1STATbits.SPIROV = 0; // clear the overflow bit
    SPI1CONbits.CKE = 1; // data changes when clock goes from hi to lo (since CKP is 0)
    SPI1CONbits.MSTEN = 1; // master operation
    SPI1CONbits.ON = 1; // turn on spi 
}


// send a byte via spi and return the response
unsigned char spi_io(unsigned char o) {
  SPI1BUF = o;
  while(!SPI1STATbits.SPIRBF) { // wait to receive the byte
    ;
 }
  return SPI1BUF;
}