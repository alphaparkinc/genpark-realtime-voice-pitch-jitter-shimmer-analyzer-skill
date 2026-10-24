import math, sys
sys.stdout.reconfigure(encoding='utf-8')

class RealtimeVoicePitchJitterShimmerAnalyzerClient:
    """
    Pure Python speech biomarker DSP analyzer.
    Calculates fundamental frequency (F0) using autocorrelation, local cycle-to-cycle
    period perturbation (Jitter %), and amplitude perturbation (Shimmer %).
    """
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        # Voice pitch search bounds: 60 Hz to 400 Hz
        self.min_lag = int(sample_rate / 400.0) # 40 samples
        self.max_lag = int(sample_rate / 60.0)  # 266 samples

    def find_pitch_periods(self, samples):
        n = len(samples)
        if n < self.max_lag * 2:
            return 0.0, []

        # Autocorrelation
        best_lag = self.min_lag
        max_corr = -1e9
        r0 = sum(s * s for s in samples[:self.max_lag])

        for lag in range(self.min_lag, min(self.max_lag, n // 2)):
            corr = 0.0
            for i in range(lag, n - lag):
                corr += samples[i] * samples[i - lag]
            if corr > max_corr:
                max_corr = corr
                best_lag = lag

        f0 = (self.sample_rate / float(best_lag)) if best_lag > 0 else 0.0

        # Segment into individual pitch periods of length best_lag
        periods = []
        for i in range(0, n - best_lag, best_lag):
            window = samples[i:i + best_lag]
            peak = max(abs(x) for x in window)
            periods.append({"length": best_lag, "amplitude": peak})

        return round(f0, 1), periods

    def analyze_vocal_biomarkers(self, samples):
        if not samples or len(samples) < 320:
            return {"status": "error", "message": "Insufficient audio samples (min 320)"}

        f0, periods = self.find_pitch_periods(samples)
        k = len(periods)
        if k < 3 or f0 < 50.0:
            return {
                "status": "success",
                "voiced_speech_detected": False,
                "fundamental_frequency_hz": 0.0,
                "jitter_local_pct": 0.0,
                "shimmer_local_pct": 0.0,
                "vocal_strain_index": 0.0,
                "clinical_state": "UNVOICED_OR_SILENCE"
            }

        # Jitter calculation: cycle-to-cycle length perturbation
        # In stationary frames, jitter is measured on micro-deviations
        diff_lengths = sum(abs(periods[i]["length"] - periods[i - 1]["length"]) for i in range(1, k))
        avg_length = sum(p["length"] for p in periods) / float(k)
        jitter_pct = (diff_lengths / float(k - 1)) / max(1e-5, avg_length) * 100.0

        # Shimmer calculation: cycle-to-cycle amplitude perturbation
        diff_amps = sum(abs(periods[i]["amplitude"] - periods[i - 1]["amplitude"]) for i in range(1, k))
        avg_amp = sum(p["amplitude"] for p in periods) / float(k)
        shimmer_pct = (diff_amps / float(k - 1)) / max(1e-5, avg_amp) * 100.0

        # Vocal strain index (0-100)
        # Normal healthy speech: Jitter < 1.04%, Shimmer < 3.81%
        strain_score = min(100.0, (jitter_pct * 30.0) + (shimmer_pct * 12.0))
        
        if strain_score > 65.0:
            classification = "HIGH_STRESS_OR_HOARSENESS"
        elif strain_score > 35.0:
            classification = "MODERATE_VOCAL_FATIGUE"
        else:
            classification = "HEALTHY_STABLE_PHONATION"

        return {
            "status": "success",
            "voiced_speech_detected": True,
            "fundamental_frequency_hz": f0,
            "pitch_period_samples": periods[0]["length"],
            "detected_pitch_cycles": k,
            "jitter_local_pct": round(jitter_pct, 3),
            "shimmer_local_pct": round(shimmer_pct, 3),
            "vocal_strain_index": round(strain_score, 1),
            "clinical_state": classification
        }
