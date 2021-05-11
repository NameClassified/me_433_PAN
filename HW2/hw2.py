import csv
import numpy as np
import matplotlib.pyplot as plt
import queue

class Signal:
    def __init__(self, times, values):
        self.times = times
        self.values = values
        self.Fs = 0.0
        self.frq = 0.0
        self.Y = 0.0
        self.X = 0

    def set_Y(self, new_Y):
        self.Y = new_Y
    
    def set_Fs(self, new_Fs):
        self.Fs = new_Fs

    def calculate_fft(self):
        dt = 1.0/10000.0 # 10kH
        # a constant plus 100Hz and 1000Hz
        self.Fs = len(self.times)/self.times[-1] # sample rate
        print(self.Fs)
        Ts = 1.0/self.Fs; # sampling interval
        y = self.values
        n = len(y) # length of the signal
        k = np.arange(n)
        T = n/self.Fs
        self.frq = k/T # two sides frequency range
        self.frq = self.frq[range(int(n/2))] # one side frequency range
        self.Y = np.fft.fft(y)/n # fft computing and normalization
        self.Y = self.Y[range(int(n/2))]
    
    def get_x(self):
        return self.X
    


def maf(sig, X):
    filtered_times = []
    filtered_values = []

    moving_sum = queue.Queue(X)
    qsum = 0
    for idx in range(X):
        moving_sum.put(0)

    for idx in range(len(sig.values)):
        qsum -= moving_sum.get()
        moving_sum.put(sig.values[idx])
        qsum += sig.values[idx]
        filtered_values.append(float(qsum/X))
        filtered_times.append(float(sig.times[idx]))

    maf_signal = Signal(filtered_times, filtered_values)
    maf_signal.calculate_fft()
    maf_signal.X = X
    maf_signals.append(maf_signal)
    return maf_signal

def iir(sig, A, B):
    filtered_times = []
    filtered_values = []

    current_sum = 0
    current_avg = 0
    for idx in range(len(sig.values)):


sigA_time = []
sigA_val = []
sigB_time = []
sigB_val = []
sigC_time = []
sigC_val = []
sigD_time = []
sigD_val = []


unfiltered = []
maf_signals = []
iir_signals = []
rc_signals = []


with open('sigA.csv') as f:
    # open the csv file
    reader = csv.reader(f)
    for row in reader:
        # read the rows 1 one by one
        sigA_time.append(float(row[0])) # leftmost column
        sigA_val.append(float(row[1])) # second column

with open('sigB.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        sigB_time.append(float(row[0]))
        sigB_val.append(float(row[1]))

with open('sigC.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        sigC_time.append(float(row[0]))
        sigC_val.append(float(row[1]))

with open('sigD.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        sigD_time.append(float(row[0]))
        sigD_val.append(float(row[1]))

signal_A = Signal(sigA_time, sigA_val)

signal_B = Signal(sigB_time, sigB_val)
signal_C = Signal(sigC_time, sigC_val)
signal_D = Signal(sigD_time, sigD_val)

signal_A.calculate_fft()
signal_B.calculate_fft()
signal_C.calculate_fft()
signal_D.calculate_fft()

unfiltered.append(signal_A)
unfiltered.append(signal_B)
unfiltered.append(signal_C)
unfiltered.append(signal_D)

maf_a = maf(signal_A, 2300)
maf_b = maf(signal_B, 800)
maf_c = maf(signal_C, 1000)
maf_d = maf(signal_D, 450)



### PLOTTING CODE

def plot_fft_unfiltered(sig1, sig2, sig3, sig4):
    fig, ((ax1, ax3, ax5, ax7), (ax2, ax4, ax6, ax8)) = plt.subplots(2, 4)
    fig.suptitle("Unfiltered Signals")
    ax1.set_title("Signal A Time Domain")
    ax1.plot(sig1.times, sig1.values,'b')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Amplitude')
    ax2.set_title("Signal A Frequency Domain")
    ax2.loglog(sig1.frq,abs(sig1.Y),'b') # plotting the fft
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.set_title("Signal B Time Domain")
    ax3.plot(sig2.times,sig2.values,'b')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Amplitude')
    ax4.set_title("Signal B Frequency Domain")
    ax4.loglog(sig2.frq,abs(sig2.Y),'b') # plotting the fft
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')

    ax5.set_title("Signal C Time Domain")
    ax5.plot(sig3.times,sig3.values,'b')
    ax5.set_xlabel('Time')
    ax5.set_ylabel('Amplitude')
    ax6.set_title("Signal C Frequency Domain")
    ax6.loglog(sig3.frq,abs(sig3.Y),'b') # plotting the fft
    ax6.set_xlabel('Freq (Hz)')
    ax6.set_ylabel('|Y(freq)|')

    ax7.set_title("Signal D Time Domain")
    ax7.plot(sig4.times,sig4.values,'b')
    ax7.set_xlabel('Time')
    ax7.set_ylabel('Amplitude')
    ax8.set_title("Signal D Frequency Domain")
    ax8.loglog(sig4.frq,abs(sig4.Y),'b') # plotting the fft
    ax8.set_xlabel('Freq (Hz)')
    ax8.set_ylabel('|Y(freq)|')
    plt.show()


def plot_fft_maf(unfiltered_signals, maf_signals):

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
    fig.suptitle("Moving-Average Filtered FFT Signals")
    ax1.set_title(f"Signal A FFT, {maf_signals[0].get_x()} Data Points")
    ax1.loglog(unfiltered_signals[0].frq, abs(unfiltered_signals[0].Y), color = 'black')
    ax1.loglog(maf_signals[0].frq, abs(maf_signals[0].Y), color = 'red')
    ax1.set_xlabel('Freq (Hz)')
    ax1.set_ylabel('|Y(freq)|')

    ax2.set_title(f"Signal B FFT, {maf_signals[1].get_x()} Data Points")
    ax2.loglog(unfiltered_signals[1].frq,abs(unfiltered_signals[1].Y), color = 'black')
    ax2.loglog(maf_signals[1].frq, abs(maf_signals[1].Y), color = 'red')
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.set_title(f"Signal C FFT, {maf_signals[2].get_x()} Data Points")
    ax3.loglog(unfiltered_signals[2].frq,abs(unfiltered_signals[2].Y), color = 'black')
    ax3.loglog(maf_signals[2].frq, abs(maf_signals[2].Y), color = 'red')
    ax3.set_xlabel('Freq (Hz)')
    ax3.set_ylabel('|Y(freq)|')

    ax4.set_title(f"Signal D FFT, {maf_signals[3].get_x()} Data Points")
    ax4.loglog(unfiltered_signals[3].frq,abs(unfiltered_signals[3].Y), color = 'black')
    ax4.loglog(maf_signals[3].frq, abs(maf_signals[3].Y), color = 'red')
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')
    plt.show()


def plot_fft_iir(unfiltered_signals, iir_signals):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
    fig.suptitle("IIR Filtered FFT Signals")
    ax1.set_title(f"Signal A FFT, {maf_signals[0].get_x()} Data Points")
    ax1.loglog(unfiltered_signals[0].frq, abs(unfiltered_signals[0].Y), color = 'black')
    ax1.loglog(iir_signals[0].frq, abs(iir_signals[0].Y), color = 'red')
    ax1.set_xlabel('Freq (Hz)')
    ax1.set_ylabel('|Y(freq)|')

    ax2.set_title(f"Signal B FFT, {maf_signals[1].get_x()} Data Points")
    ax2.loglog(unfiltered_signals[1].frq,abs(unfiltered_signals[1].Y), color = 'black')
    ax2.loglog(iir_signals[1].frq, abs(iir_signals[1].Y), color = 'red')
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.set_title(f"Signal C FFT, {maf_signals[2].get_x()} Data Points")
    ax3.loglog(unfiltered_signals[2].frq,abs(unfiltered_signals[2].Y), color = 'black')
    ax3.loglog(iir_signals[2].frq, abs(iir_signals[2].Y), color = 'red')
    ax3.set_xlabel('Freq (Hz)')
    ax3.set_ylabel('|Y(freq)|')

    ax4.set_title(f"Signal D FFT, {maf_signals[3].get_x()} Data Points")
    ax4.loglog(unfiltered_signals[3].frq,abs(unfiltered_signals[3].Y), color = 'black')
    ax4.loglog(iir_signals[3].frq, abs(iir_signals[3].Y), color = 'red')
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')
    plt.show()
#plot_fft_unfiltered(signal_A, signal_B, signal_C, signal_D)
plot_fft_maf(unfiltered, maf_signals)


