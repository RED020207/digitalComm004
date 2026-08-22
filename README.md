# Experiment 4: Uniform Quantization and PCM Encoding

## 1. Overview

This module explores the discrete amplitude processing of continuous-time analog signals via **Uniform Quantization** and **Pulse Code Modulation (PCM)** encoding. The objective is to evaluate how bit depth ($n$) and level allocation ($L = 2^n$) govern quantization error, granular noise distortion, and Signal-to-Quantization-Noise Ratio ($\text{SQNR}$).

---

## 2. Mathematical & Physical Principles

### 2.1. Signal Normalization & Quantization Geometry

A continuous-time sinusoid $x(t) = A \sin(2\pi f_0 t)$ is constrained to the normalized amplitude interval $[V_{\min}, V_{\max}] = [-1, +1]$, giving a full-scale dynamic range of $V_{\text{pp}} = V_{\max} - V_{\min} = 2\text{ V}$.

An $n$-bit uniform mid-rise quantizer partitions this dynamic range into $L = 2^n$ non-overlapping decision intervals of equal step size $\Delta$:

$$\Delta = \frac{V_{\max} - V_{\min}}{L} = \frac{2}{2^n} = 2^{1-n}$$

Each sample $x(t)$ is mapped to an integer index $k \in \{0, 1, \dots, L-1\}$ and reconstructed as a discrete voltage level $\hat{x}_k$:

$$\hat{x}_k = V_{\min} + \left(k + \frac{1}{2}\right)\Delta$$

$$\text{Decision Interval } I_k = [V_{\min} + k\Delta, \; V_{\min} + (k+1)\Delta)$$

```
Amplitude (V)
 +1.0  |------------------------------  Decision Boundary (L)
       |   Representation Level (L-1)  = V_min + (L - 0.5)Δ
       |------------------------------  Decision Boundary (L-1)
       |               ...
  0.0  + - - - - - - - - - - - - - - -  Zero-Crossing Axis
       |               ...
       |   Representation Level (0)    = V_min + 0.5Δ
 -1.0  |------------------------------  Decision Boundary (0)

```

---

### 2.2. PCM Bit Stream Generation

The quantizer index $k$ is mapped to a unique $n$-bit binary word through standard Pulse Code Modulation (PCM):

$$k \xrightarrow{\text{PCM}} \mathbf{b} = [b_{n-1}, b_{n-2}, \dots, b_0]_2, \quad b_i \in \{0, 1\}$$

The system bit rate $R_b$ required for transmission at sampling frequency $f_s$ is:

$$R_b = n \cdot f_s \quad (\text{bits/sec})$$

---

### 2.3. Theoretical SQNR Derivation ($6.02n + 1.76\text{ dB}$)

1. **Signal Power ($P_s$):**
For a normalized sinusoid $x(t) = \sin(\omega_0 t)$ with peak amplitude $A = 1$:
$$P_s = \frac{1}{T} \int_{0}^{T} \sin^2(\omega_0 t) \, dt = \frac{A^2}{2} = 0.5 \text{ W}$$


2. **Quantization Noise Power ($P_e$):**
Assuming the quantization error $e(t) = x(t) - x_q(t)$ is uniformly distributed over $[-\Delta/2, +\Delta/2]$ with probability density function $f_E(e) = \frac{1}{\Delta}$:
$$P_e = \mathbb{E}[E^2] = \int_{-\Delta/2}^{+\Delta/2} e^2 \cdot \frac{1}{\Delta} \, de = \left[ \frac{e^3}{3\Delta} \right]_{-\Delta/2}^{+\Delta/2} = \frac{\Delta^2}{12}$$


Substituting $\Delta = \frac{2}{2^n}$:
$$P_e = \frac{\left(\frac{2}{2^n}\right)^2}{12} = \frac{4 \cdot 2^{-2n}}{12} = \frac{2^{-2n}}{3}$$


3. **SQNR Calculation:**
$$\text{SQNR}_{\text{linear}} = \frac{P_s}{P_e} = \frac{0.5}{\frac{2^{-2n}}{3}} = 1.5 \times 2^{2n}$$


Converting to decibels:
$$\text{SQNR}_{\text{dB}} = 10 \log_{10}\left(1.5 \times 2^{2n}\right) = 10 \log_{10}(1.5) + 10 \log_{10}\left(2^{2n}\right)$$


$$\text{SQNR}_{\text{dB}} = 1.7609 + 20n \log_{10}(2) \approx \mathbf{6.02n + 1.76 \text{ dB}}$$



---

## 3. Implementation Workflow

The implementation steps for discrete processing and data flow are outlined below:

```
+--------------------------+
| Continuous Input Signal  |  x(t) = sin(2π f0 t)
+--------------------------+
             |
             v
+--------------------------+
|  Mid-Rise Quantization   |  k = floor((x - V_min) / Δ)
+--------------------------+
             |
             v
+--------------------------+  Representation Reconstruction
| Reconstructed Waveform   |  x_q = V_min + (k + 0.5)Δ
+--------------------------+
             |
             +-----------------------+
             |                       |
             v                       v
+--------------------------+  +--------------------------+
|   PCM Binary Encoding    |  |    Statistical Analysis  |
|   k -> n-bit string      |  |    e(t) = x(t) - x_q(t)  |
+--------------------------+  +--------------------------+

```

### Algorithmic Logic

```python
# Step 1: Compute decision index k with boundary protection
raw_indices = np.floor((x - v_min) / delta).astype(int)
indices = np.clip(raw_indices, 0, L - 1)

# Step 2: Mid-rise level reconstruction
representation_levels = v_min + (np.arange(L) + 0.5) * delta
x_q = representation_levels[indices]

# Step 3: PCM encoding
pcm_words = [format(idx_val, f'0{n}b') for idx_val in indices]

# Step 4: Empirical SQNR computation
e = x - x_q
p_signal = np.mean(x**2)
p_noise = np.mean(e**2)
sqnr_measured = 10 * np.log10(p_signal / p_noise)

```

---

## 4. Empirical Validation & Results

The simulation executed strict validation tests across 5 bit configurations ($n \in \{2, 3, 4, 6, 8\}$).

### Validation & SQNR Summary

| Bit Depth ($n$) | Levels ($L$) | Index Bounds Check $[0, L-1]$ | PCM Word Length ($n$) | Measured SQNR ($\text{dB}$) | Theoretical SQNR ($\text{dB}$) | Discrepancy $\Delta_{\text{SQNR}}$ ($\text{dB}$) |
| --- | --- | --- | --- | --- | --- | --- |
| **2** | 4 | **PASSED** | **PASSED** | 12.81 | 13.80 | **0.99** |
| **3** | 8 | **PASSED** | **PASSED** | 19.09 | 19.82 | **0.73** |
| **4** | 16 | **PASSED** | **PASSED** | 25.31 | 25.84 | **0.53** |
| **6** | 64 | **PASSED** | **PASSED** | 37.61 | 37.88 | **0.27** |
| **8** | 256 | **PASSED** | **PASSED** | 49.79 | 49.92 | **0.13** |

---

## 5. Discrepancy & Diagnostic Analysis

### 5.1. Observation

At low resolutions ($n = 2$), the measured SQNR ($12.81\text{ dB}$) exhibits a **$0.99\text{ dB}$ deviation** from the theoretical prediction ($13.80\text{ dB}$). As $n$ increases, this error drops monotonically to **$0.13\text{ dB}$ at $n = 8$**.

```
  Discrepancy (dB)
   1.0 +-- * (0.99 dB at n=2)
       |    \
   0.8 |--   * (0.73 dB at n=3)
       |      \
   0.6 |--     * (0.53 dB at n=4)
       |        \
   0.4 |--       \
   0.2 |--        *-------* (0.27 dB at n=6 -> 0.13 dB at n=8)
   0.0 +---+-------+-------+-------+
           2       4       6       8   Bits (n)

```

### 5.2. Root Cause Analysis

The theoretical equation $\text{SQNR} = 6.02n + 1.76\text{ dB}$ depends on **Bennett's Quantization Noise Hypotheses**:

1. The error $e(t)$ is uniformly distributed over $[-\Delta/2, +\Delta/2]$.
2. The error $e(t)$ is uncorrelated with the input signal $x(t)$.

For continuous sinusoidal signals $x(t) = \sin(\omega_0 t)$, the signal derivative satisfies:

$$\frac{dx}{dt} = \omega_0 \cos(\omega_0 t)$$

At signal peaks ($x(t) \to \pm 1$), $\frac{dx}{dt} \to 0$. This zero slope causes the signal amplitude to remain within the extreme decision intervals for an extended portion of each period.

* **For $n = 2$ ($L = 4$):** The step size $\Delta = 0.5\text{ V}$ is large relative to the signal amplitude. The peak dwell time forces quantization error $e(t)$ to cluster heavily near the boundaries of the error interval, violating the uniform distribution assumption $U[-\Delta/2, \Delta/2]$.
* **For $n \ge 4$ ($L \ge 16$):** The step size $\Delta \le 0.125\text{ V}$ is small enough that the signal traverses many decision thresholds rapidly. This restores a uniform error distribution and aligns empirical performance with the theoretical model.

---

## 6. Execution Instructions

Run the entire implementation within a single **Google Colab** cell or locally:

```bash
pip install numpy matplotlib
python experiment_4_pcm.py

```
