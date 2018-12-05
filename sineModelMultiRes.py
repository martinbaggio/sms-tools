def sineModelMultiRes(x, fs, w1, w2, w3, N1, N2, N3, t, B1, B2, B3):
    """
    Analysis/synthesis of a sound using the multi resolution sinusoidal model, without sine tracking
    x: input array sound, w1, w2 & w3: analysis window, N1, N2, & N3: size of complex spectrum, t: threshold in negative dB
    B1, B2, & B3: different bandwith for given windows
    returns y: output array sound
    """
    import dftModel as DFT
    import utilFunctions as UF				# sms-tool https://github.com/MTG/sms-tools
    import numpy as np

    w = [w1, w2, w3]                                    # build the arrays for loop
    N = [N1, N2, N3]
    plocinic = [0, np.floor(B1 * N2 / fs), np.floor(B2 * N3 / fs)]   #ploc inicial for all B
    plocfin = [np.ceil(B1 * N1 / fs), np.ceil(B2 * N2 / fs), np.ceil(B3 * N3 / fs)] #ploc final for all B
    signal = np.zeros(len(x))                           # build the output signal
    for i in range(3):
        hM1 = int(math.floor((w[i].size + 1) / 2))      # half analysis window size by rounding
        hM2 = int(math.floor(w[i].size / 2))            # half analysis window size by floor
        Ns = N[i]                                       # FFT size for synthesis (even)
        H = Ns // 4                                     # Hop size used for analysis and synthesis
        hNs = Ns // 2                                   # half of synthesis FFT size
        pin = max(hNs, hM1)                             # init sound pointer in middle of anal window
        pend = x.size - max(hNs, hM1)                   # last sample to start a frame
        fftbuffer = np.zeros(N[i])                      # initialize buffer for FFT
        yw = np.zeros(Ns)                               # initialize output sound frame
        y = np.zeros(x.size)                            # initialize output array
        w[i] = w[i] / sum(w[i])                         # normalize analysis window
        sw = np.zeros(Ns)                               # initialize synthesis window
        ow = triang(2 * H)                              # triangular window
        sw[hNs - H:hNs + H] = ow                        # add triangular windows
        bh = blackmanharris(Ns)                         # blackmanharris window
        bh = bh / sum(bh)                               # normalized blackmanharris window
        sw[hNs - H:hNs + H] = sw[hNs - H:hNs + H] / bh[hNs - H:hNs + H]  # normalized synthesis window
        while pin < pend:                               # while input sound pointer is within sound
            # -----analysis-----
            x1 = x[pin - hM1:pin + hM2]                 # select frame
            mX, pX = DFT.dftAnal(x1, w[i], N[i])        # compute dft
            ploc = UF.peakDetection(mX, t)              # detect locations of peaks
            ploc = ploc[(ploc >= plocinic[i]) & (ploc <= plocfin[i])] # filter ploc's out of range B
            iploc, ipmag, ipphase = UF.peakInterp(mX, pX, ploc)  # refine peak values by interpolation
            ipfreq = fs * iploc / float(N[i])
            # -----synthesis-----
            Y = UF.genSpecSines(ipfreq, ipmag, ipphase, Ns, fs)  # generate sines in the spectrum
            fftbuffer = np.real(ifft(Y))                # compute inverse FFT
            yw[:hNs - 1] = fftbuffer[hNs + 1:]          # undo zero-phase window
            yw[hNs - 1:] = fftbuffer[:hNs + 1]
            y[pin - hNs:pin + hNs] += sw * yw           # overlap-add and apply a synthesis window
            pin += H                                    # advance sound pointer
        signal = signal + y                             # sum of signals at different bandwith
    return signal
