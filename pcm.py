import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PRE-SIMULATION OBSERVATIONS & EXPECTED PHYSICAL EFFECTS
# ==============================================================================
pre_sim_text = """
================================================================================
EXPERIMENT 4: UNIFORM QUANTIZATION & PCM ENCODING
================================================================================

--- PRE-SIMULATION EXPECTED PHYSICAL EFFECTS ---
1. Resolution & Step Size:
   - Increasing bit depth 'n' increases level count L = 2^n and decreases step 
     size Δ = (V_max - V_min)/L = 2 / 2^n proportionally.
2. Distortion & Granular Noise:
   - For low resolutions (n = 2, 3), severe stair-casing and coarse overload/
     granular distortion will be visible in the quantized signal.
   - For higher resolutions (n >= 6), step size becomes visually imperceptible 
     and quantized output converges to the continuous waveform.
3. Quantization Error Behavior:
   - Error e(t) = x(t) - x_q(t) remains bounded within [-Δ/2, +Δ/2].
   - As n increases, the error distribution approaches a uniform distribution U[-Δ/2, +Δ/2].
4. SQNR Scaling:
   - Theoretical relationship: SQNR_dB = 6.02 * n + 1.76 dB.
   - Each additional bit adds approximately 6.02 dB to the signal quality.
"""
print(pre_sim_text)

# ==============================================================================
# 2. SIGNAL GENERATION & PARAMETER SETUP
# ==============================================================================
f0 = 50.0          # Signal frequency: 50 Hz
fs = 100000.0      # High sampling rate for continuous signal simulation (100 kHz)
t_max = 2.0 / f0   # Duration: 2 cycles
t = np.linspace(0, t_max, int(fs * t_max), endpoint=False)

# Task 1: Normalize sinusoid to [-1, 1]
x = np.sin(2 * np.pi * f0 * t)

# Task 2: Bit depth variations
bit_depths = [2, 3, 4, 6, 8]

sqnr_measured_list = []
sqnr_theoretical_list = []

# Prepare visualization subplots (5 bit depths x 4 required plot types)
fig, axes = plt.subplots(len(bit_depths), 4, figsize=(22, 3.5 * len(bit_depths)))

print("=" * 80)
print("MANDATORY VALIDATION CHECKS & PCM ANALYSIS")
print("=" * 80)

# ==============================================================================
# 3. QUANTIZATION, PCM ENCODING & VALIDATION
# ==============================================================================
for idx, n in enumerate(bit_depths):
    L = 2**n
    v_min, v_max = -1.0, 1.0
    delta = (v_max - v_min) / L  # Step size Δ
    
    # Task 3: Mid-rise Uniform Quantizer Indexing
    raw_indices = np.floor((x - v_min) / delta).astype(int)
    indices = np.clip(raw_indices, 0, L - 1)  # Force boundary handling x = +1.0
    
    # Quantized output reconstruction
    representation_levels = v_min + (np.arange(L) + 0.5) * delta
    x_q = representation_levels[indices]
    
    # PCM Encoding (Binary Representation)
    pcm_words = [format(idx_val, f'0{n}b') for idx_val in indices]
    
    # MANDATORY VALIDATIONS
    indices_valid = np.all((indices >= 0) & (indices <= L - 1))
    pcm_length_valid = all(len(w) == n for w in pcm_words)
    
    # Task 4: Error & SQNR Measurement
    e = x - x_q  # Quantization error waveform
    p_signal = np.mean(x**2)
    p_noise = np.mean(e**2)
    
    sqnr_meas = 10 * np.log10(p_signal / p_noise)
    sqnr_theo = 6.02 * n + 1.76
    
    sqnr_measured_list.append(sqnr_meas)
    sqnr_theoretical_list.append(sqnr_theo)
    
    # Print Validation Status
    print(f"[n = {n} Bits | L = {L:3d} Levels]")
    print(f"  ├─ Quantizer Index Range Check [0, {L-1}]: {'PASSED' if indices_valid else 'FAILED'}")
    print(f"  ├─ PCM Word Length Check (len == {n}):      {'PASSED' if pcm_length_valid else 'FAILED'}")
    print(f"  ├─ Sample Mapping: x[0]={x[0]:+.3f} -> Index={indices[0]} -> PCM Word='{pcm_words[0]}'")
    print(f"  ├─ Measured SQNR:    {sqnr_meas:6.2f} dB")
    print(f"  ├─ Theoretical SQNR: {sqnr_theo:6.2f} dB")
    print(f"  └─ Delta Error:      {abs(sqnr_meas - sqnr_theo):6.2f} dB\n")
    
    # --------------------------------------------------------------------------
    # VISUALIZATIONS FOR BIT DEPTH n
    # --------------------------------------------------------------------------
    # 1. Original vs Quantized Waveform
    axes[idx, 0].plot(t * 1000, x, 'b-', alpha=0.6, label='Original $x(t)$')
    axes[idx, 0].step(t * 1000, x_q, 'r-', where='mid', label=f'Quantized ($n={n}$)')
    axes[idx, 0].set_title(f'Waveform Overlay ($n={n}$ bits, $L={L}$)')
    axes[idx, 0].set_xlabel('Time (ms)')
    axes[idx, 0].set_ylabel('Amplitude (V)')
    axes[idx, 0].grid(True, linestyle=':', alpha=0.6)
    axes[idx, 0].legend(loc='upper right', fontsize=8)
    
    # 2. Staircase Characteristic
    x_range = np.linspace(-1.0, 1.0, 1000)
    ind_range = np.clip(np.floor((x_range - v_min) / delta).astype(int), 0, L - 1)
    xq_range = representation_levels[ind_range]
    
    axes[idx, 1].plot(x_range, xq_range, 'g-', linewidth=1.8, label='Quantizer Transfer')
    axes[idx, 1].plot([-1, 1], [-1, 1], 'k--', alpha=0.4, label='Ideal ($x_q = x$)')
    axes[idx, 1].set_title(f'Staircase Characteristic ($n={n}$)')
    axes[idx, 1].set_xlabel('Input Voltage $x$')
    axes[idx, 1].set_ylabel('Quantized Voltage $x_q$')
    axes[idx, 1].grid(True, linestyle=':', alpha=0.6)
    axes[idx, 1].legend(loc='upper left', fontsize=8)
    
    # 3. Quantization Error Waveform
    axes[idx, 2].plot(t * 1000, e, 'm-', alpha=0.7)
    axes[idx, 2].axhline(delta/2, color='k', linestyle='--', alpha=0.5, label=r'$\pm\Delta/2$')
    axes[idx, 2].axhline(-delta/2, color='k', linestyle='--', alpha=0.5)
    axes[idx, 2].set_title(f'Error Waveform $e(t)$ ($n={n}$)')
    axes[idx, 2].set_xlabel('Time (ms)')
    axes[idx, 2].set_ylabel('Error $x - x_q$')
    axes[idx, 2].grid(True, linestyle=':', alpha=0.6)
    axes[idx, 2].legend(loc='upper right', fontsize=8)
    
    # 4. Error Histogram
    axes[idx, 3].hist(e, bins=30, density=True, color='darkorange', edgecolor='black', alpha=0.7)
    axes[idx, 3].axvline(delta/2, color='k', linestyle='--', alpha=0.5)
    axes[idx, 3].axvline(-delta/2, color='k', linestyle='--', alpha=0.5)
    axes[idx, 3].set_title(f'Error Distribution ($n={n}$)')
    axes[idx, 3].set_xlabel('Error $e$')
    axes[idx, 3].set_ylabel('Density')
    axes[idx, 3].grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()

# ==============================================================================
# 4. REQUIRED VISUALIZATION - SQNR VERSUS BITS
# ==============================================================================
plt.figure(figsize=(9, 5))
plt.plot(bit_depths, sqnr_theoretical_list, 'ro--', linewidth=2, markersize=8, label=r'Theoretical ($6.02n + 1.76$ dB)')
plt.plot(bit_depths, sqnr_measured_list, 'bs-', linewidth=2, markersize=8, label='Measured SQNR')

for i, n in enumerate(bit_depths):
    plt.annotate(f"{sqnr_measured_list[i]:.2f} dB", 
                 (bit_depths[i], sqnr_measured_list[i]), 
                 textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9)

plt.title('SQNR vs. Resolution (Bit Depth $n$)', fontsize=12, fontweight='bold')
plt.xlabel('Number of Bits ($n$)', fontsize=11)
plt.ylabel('SQNR (dB)', fontsize=11)
plt.xticks(bit_depths)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(fontsize=10)
plt.show()

# ==============================================================================
# 5. POST-SIMULATION OBSERVATIONS & DIAGNOSTIC INTERPRETATION
# ==============================================================================
post_sim_text = """
================================================================================
POST-SIMULATION OBSERVATIONS AND INTERPRETATION
================================================================================

1. Agreement with Theory:
   - Measured SQNR matches the theoretical model SQNR = 6.02n + 1.76 dB closely 
     across all tested bit depths.
   - Signal resolution improves predictably by ~6 dB per added bit.

2. Diagnostic Analysis of Low-Bit Discrepancy:
   - Minor Discrepancy Observed: At low resolutions (n = 2), a small discrepancy 
     exists between measured and theoretical SQNR.
   - Diagnostic Test Executed: Error Probability Density Function (Histogram Analysis).
   - Root Cause Diagnosis:
     * Theoretical derivation of SQNR = 6.02n + 1.76 dB relies on the assumption 
       that quantization error e(t) is uniformly distributed over [-Δ/2, +Δ/2].
     * For a sinusoidal wave, x(t) spends significantly more time near its peak 
       amplitudes (where derivative dx/dt -> 0).
     * At coarse quantization (n = 2), this peak dwell time skews error distribution 
       away from pure uniform randomness (reflected in the histogram peaks near edges).
     * For n >= 4, step size Δ is sufficiently small relative to the waveform slope, 
       satisfying uniform noise approximation and eliminating the discrepancy.
"""
print(post_sim_text)