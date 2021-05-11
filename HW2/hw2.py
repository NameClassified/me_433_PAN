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
        self.A = 0
        self.B = 0
        self.nweights = 0
        self.cutoff = 0
        self.band = 0

    def set_Y(self, new_Y):
        self.Y = new_Y
    
    def set_Fs(self, new_Fs):
        self.Fs = new_Fs

    def calculate_fft(self):
        dt = 1.0/10000.0 # 10kH
        # a constant plus 100Hz and 1000Hz
        self.Fs = len(self.times)/self.times[-1] # sample rate
        #print(self.Fs)
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

    def get_a(self):
        return self.A

    def get_b(self):
        return self.B
    
    def get_nweights(self):
        return self.nweights
    
    def get_cutoff(self):
        return self.cutoff
    
    def get_band(self):
        return self.band

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
    
    current_avg = 0
    for idx in range(len(sig.values)):

        weight_b = sig.values[idx]*B
        if (idx == 0):
            weight_a = 0
        else:
            weight_a = filtered_values[idx-1]*A
        current_avg = weight_a+weight_b
        filtered_values.append(current_avg)
        filtered_times.append(sig.times[idx])
    iir_signal = Signal(filtered_times, filtered_values)
    iir_signal.A = A
    iir_signal.B = B
    iir_signal.calculate_fft()
    iir_signals.append(iir_signal)
    return iir_signal

def map_weights(a,b):
    return a*b

def fir(sig, weights, cutoff, bandwidth, X):
    filtered_times = []
    filtered_values = []
    q = []
    
    for idx in range(X):
        q.append(0)
    
    current_sum = 0

    for idx in range(len(sig.values)):
        q.pop(0)
        q.append(sig.values[idx])
        current_sum = sum(map(map_weights, q, weights))
        filtered_values.append(current_sum)
        filtered_times.append(sig.times[idx])
    fir_signal = Signal(filtered_times, filtered_values)
    fir_signal.calculate_fft()
    fir_signal.X = X
    fir_signal.cutoff = cutoff
    fir_signal.band = bandwidth
    fir_signal.nweights = len(weights)
    fir_signals.append(fir_signal)

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
fir_signals = []

def read_csvs():
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

def generate_signals():
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

    iir_a = iir(signal_A, 0.999, 0.001)
    iir_b = iir(signal_B, 0.995, 0.005)
    iir_c = iir(signal_C, 0.2, 0.8)
    iir_d = iir(signal_D, 0.95, 0.05)

    #4, 16, 79
    w_B = [
    0.000576110880220521,
    0.000646822448048742,
    0.000746173886528511,
    0.000880485495847452,
    0.001055865380883305,
    0.001278093218249943,
    0.001552506461458987,
    0.001883890946839809,
    0.002276377817745797,
    0.002733348606047448,
    0.003257350199003677,
    0.003850021277918203,
    0.004512031644686462,
    0.005243035656095933,
    0.006041640766708672,
    0.006905391942899444,
    0.007830772457077449,
    0.008813221306509297,
    0.009847167229931069,
    0.010926079021878313,
    0.012042531574028448,
    0.013188286809477480,
    0.014354388424299893,
    0.015531269115327082,
    0.016708868757928562,
    0.017876761806466711,
    0.019024292026397268,
    0.020140712533626107,
    0.021215329016118584,
    0.022237643946748514,
    0.023197499566239548,
    0.024085217421448386,
    0.024891732287200149,
    0.025608718378814715,
    0.026228705876144665,
    0.026745185926567137,
    0.027152702471551313,
    0.027446929446248967,
    0.027624732130639769,
    0.027684211680294977,
    0.027624732130639772,
    0.027446929446248970,
    0.027152702471551313,
    0.026745185926567140,
    0.026228705876144665,
    0.025608718378814715,
    0.024891732287200156,
    0.024085217421448389,
    0.023197499566239552,
    0.022237643946748514,
    0.021215329016118580,
    0.020140712533626110,
    0.019024292026397261,
    0.017876761806466707,
    0.016708868757928565,
    0.015531269115327082,
    0.014354388424299898,
    0.013188286809477487,
    0.012042531574028448,
    0.010926079021878319,
    0.009847167229931078,
    0.008813221306509298,
    0.007830772457077454,
    0.006905391942899445,
    0.006041640766708676,
    0.005243035656095938,
    0.004512031644686464,
    0.003850021277918208,
    0.003257350199003678,
    0.002733348606047450,
    0.002276377817745797,
    0.001883890946839810,
    0.001552506461458987,
    0.001278093218249943,
    0.001055865380883304,
    0.000880485495847452,
    0.000746173886528511,
    0.000646822448048742,
    0.000576110880220521,
    ]


    w_C = [
    -0.000837774890188407,
    -0.000793458226766910,
    -0.000769578287591838,
    -0.000730029063487416,
    -0.000627265902180834,
    -0.000404709606106469,
    0.000000000000000000,
    0.000651077132119953,
    0.001610217854369899,
    0.002932049213442453,
    0.004659688323587644,
    0.006820703792947220,
    0.009423756708600777,
    0.012456164858110453,
    0.015882583756646095,
    0.019644934288517830,
    0.023663633220235899,
    0.027840104058494901,
    0.032060466677011658,
    0.036200229871446055,
    0.040129746325203552,
    0.043720138619493490,
    0.046849371289725592,
    0.049408129831910237,
    0.051305174076467723,
    0.052471860238192038,
    0.052865571679596830,
    0.052471860238192038,
    0.051305174076467723,
    0.049408129831910237,
    0.046849371289725605,
    0.043720138619493497,
    0.040129746325203552,
    0.036200229871446055,
    0.032060466677011665,
    0.027840104058494911,
    0.023663633220235902,
    0.019644934288517834,
    0.015882583756646102,
    0.012456164858110453,
    0.009423756708600775,
    0.006820703792947224,
    0.004659688323587644,
    0.002932049213442455,
    0.001610217854369901,
    0.000651077132119953,
    0.000000000000000000,
    -0.000404709606106469,
    -0.000627265902180834,
    -0.000730029063487417,
    -0.000769578287591838,
    -0.000793458226766910,
    -0.000837774890188407,
    ]

    #12, 60, 31
    w_D = [
    0.000000000000000000,
    0.000066176882674908,
    0.000394078409893385,
    0.001238358864351943,
    0.002944727417763975,
    0.005929694875278317,
    0.010614539881640135,
    0.017320457505890275,
    0.026147577496678447,
    0.036871080818180614,
    0.048888966700460980,
    0.061246746285470575,
    0.072746331240894177,
    0.082124353088736501,
    0.088265311761849166,
    0.090403197540473129,
    0.088265311761849166,
    0.082124353088736501,
    0.072746331240894177,
    0.061246746285470610,
    0.048888966700461008,
    0.036871080818180621,
    0.026147577496678481,
    0.017320457505890292,
    0.010614539881640142,
    0.005929694875278317,
    0.002944727417763972,
    0.001238358864351943,
    0.000394078409893384,
    0.000066176882674908,
    0.000000000000000000,
    ]

    #8, 16, 79, HAMMING
    w_A = [
    -0.000649596913047532,
    -0.000690004129086553,
    -0.000747482712281249,
    -0.000821312397550319,
    -0.000908207332465903,
    -0.001002177679221514,
    -0.001094501143736012,
    -0.001173810694454979,
    -0.001226300477147285,
    -0.001236047487823510,
    -0.001185442096234863,
    -0.001055716183429074,
    -0.000827553632330127,
    -0.000481764345508873,
    0.000000000000000001,
    0.000634512493918529,
    0.001436245288402773,
    0.002416677646637531,
    0.003583663361279126,
    0.004940881853443106,
    0.006487395062527999,
    0.008217329206062871,
    0.010119696721431155,
    0.012178369320100224,
    0.014372208235926937,
    0.016675352596891537,
    0.019057661571728838,
    0.021485300723360294,
    0.023921458023641509,
    0.026327170425803331,
    0.028662237915922848,
    0.030886198717404893,
    0.032959336922784715,
    0.034843692366105967,
    0.036504042085098089,
    0.037908823279000865,
    0.039030969232979197,
    0.039848632205931649,
    0.040345770683454074,
    0.040512582568959572,
    0.040345770683454074,
    0.039848632205931656,
    0.039030969232979197,
    0.037908823279000872,
    0.036504042085098089,
    0.034843692366105967,
    0.032959336922784722,
    0.030886198717404899,
    0.028662237915922859,
    0.026327170425803331,
    0.023921458023641505,
    0.021485300723360298,
    0.019057661571728831,
    0.016675352596891537,
    0.014372208235926940,
    0.012178369320100224,
    0.010119696721431159,
    0.008217329206062874,
    0.006487395062527999,
    0.004940881853443107,
    0.003583663361279129,
    0.002416677646637532,
    0.001436245288402774,
    0.000634512493918530,
    0.000000000000000001,
    -0.000481764345508874,
    -0.000827553632330127,
    -0.001055716183429075,
    -0.001185442096234863,
    -0.001236047487823511,
    -0.001226300477147285,
    -0.001173810694454980,
    -0.001094501143736012,
    -0.001002177679221514,
    -0.000908207332465902,
    -0.000821312397550319,
    -0.000747482712281249,
    -0.000690004129086553,
    -0.000649596913047532,
    ]

    
    
    fir_a = fir(signal_A, w_B, 4, 16, 79)
    fir_b = fir(signal_B, w_B, 4, 16, 79)
    fir_c = fir(signal_C, w_C, 10, 24, 53)
    fir_d = fir(signal_D, w_D, 12, 60, 31)

read_csvs()
generate_signals()


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
    ax1.set_title(f"Signal A FFT, A = {iir_signals[0].get_a()}, B = {iir_signals[0].get_b()}")
    ax1.loglog(unfiltered_signals[0].frq, abs(unfiltered_signals[0].Y), color = 'black')
    ax1.loglog(iir_signals[0].frq, abs(iir_signals[0].Y), color = 'red')
    ax1.set_xlabel('Freq (Hz)')
    ax1.set_ylabel('|Y(freq)|')

    ax2.set_title(f"Signal B FFT, A = {iir_signals[1].get_a()}, B = {iir_signals[1].get_b()}")
    ax2.loglog(unfiltered_signals[1].frq,abs(unfiltered_signals[1].Y), color = 'black')
    ax2.loglog(iir_signals[1].frq, abs(iir_signals[1].Y), color = 'red')
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.set_title(f"Signal C FFT, A = {iir_signals[2].get_a()}, B = {iir_signals[2].get_b()}")
    ax3.loglog(unfiltered_signals[2].frq,abs(unfiltered_signals[2].Y), color = 'black')
    ax3.loglog(iir_signals[2].frq, abs(iir_signals[2].Y), color = 'red')
    ax3.set_xlabel('Freq (Hz)')
    ax3.set_ylabel('|Y(freq)|')

    ax4.set_title(f"Signal D FFT, A = {iir_signals[3].get_a()}, B = {iir_signals[3].get_b()}")
    ax4.loglog(unfiltered_signals[3].frq,abs(unfiltered_signals[3].Y), color = 'black')
    ax4.loglog(iir_signals[3].frq, abs(iir_signals[3].Y), color = 'red')
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')
    plt.show()

def plot_fft_fir(unfiltered_signals, fir_signals):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
    fig.suptitle("FIR Filtered FFT Signals")
    ax1.set_title(f"Signal A FFT, nweights = {fir_signals[0].get_nweights()}, cutoff = {fir_signals[0].get_cutoff()}, bandwidth = {fir_signals[0].get_band()}")
    ax1.loglog(unfiltered_signals[0].frq, abs(unfiltered_signals[0].Y), color = 'black')
    ax1.loglog(fir_signals[0].frq, abs(fir_signals[0].Y), color = 'red')
    ax1.set_xlabel('Freq (Hz)')
    ax1.set_ylabel('|Y(freq)|')

    ax2.set_title(f"Signal B FFT, nweights = {fir_signals[1].get_nweights()}, cutoff = {fir_signals[1].get_cutoff()}, bandwidth = {fir_signals[1].get_band()}")
    ax2.loglog(unfiltered_signals[1].frq,abs(unfiltered_signals[1].Y), color = 'black')
    ax2.loglog(fir_signals[1].frq, abs(fir_signals[1].Y), color = 'red')
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.set_title(f"Signal C FFT, nweights = {fir_signals[2].get_nweights()}, cutoff = {fir_signals[2].get_cutoff()}, bandwidth = {fir_signals[2].get_band()}")
    ax3.loglog(unfiltered_signals[2].frq,abs(unfiltered_signals[2].Y), color = 'black')
    ax3.loglog(fir_signals[2].frq, abs(fir_signals[2].Y), color = 'red')
    ax3.set_xlabel('Freq (Hz)')
    ax3.set_ylabel('|Y(freq)|')

    ax4.set_title(f"Signal D FFT, nweights = {fir_signals[3].get_nweights()}, cutoff = {fir_signals[3].get_cutoff()}, bandwidth = {fir_signals[3].get_band()}")
    ax4.loglog(unfiltered_signals[3].frq,abs(unfiltered_signals[3].Y), color = 'black')
    ax4.loglog(fir_signals[3].frq, abs(fir_signals[3].Y), color = 'red')
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')
    plt.show()

#plot_fft_unfiltered(signal_A, signal_B, signal_C, signal_D)
#plot_fft_maf(unfiltered, maf_signals)
#plot_fft_iir(unfiltered, iir_signals)
plot_fft_fir(unfiltered, fir_signals)