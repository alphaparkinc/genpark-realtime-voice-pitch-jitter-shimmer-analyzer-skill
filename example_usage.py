from client import RealtimeVoicePitchJitterShimmerAnalyzerClient
import math, sys
sys.stdout.reconfigure(encoding='utf-8')

def generate_voice_frame(freq=180.0, sample_rate=16000, duration_sec=0.08, amp_mod=0.05):
    n = int(sample_rate * duration_sec)
    samples = []
    for i in range(n):
        t = i / float(sample_rate)
        # Fundamental + 2nd harmonic + slight amplitude tremor
        env = 18000.0 * (1.0 + amp_mod * math.sin(2.0 * math.pi * 12.0 * t))
        val = env * (0.8 * math.sin(2.0 * math.pi * freq * t) + 0.2 * math.sin(4.0 * math.pi * freq * t))
        samples.append(val)
    return samples

def main():
    analyzer = RealtimeVoicePitchJitterShimmerAnalyzerClient(sample_rate=16000)
    print("=== REALTIME VOICE PITCH JITTER & SHIMMER ANALYZER ===")
    
    # 1. Stable speech phonation (180 Hz)
    stable_frame = generate_voice_frame(freq=180.0, amp_mod=0.02)
    res_stable = analyzer.analyze_vocal_biomarkers(stable_frame)
    print(f"1. Stable Speech: F0={res_stable['fundamental_frequency_hz']} Hz | Jitter={res_stable['jitter_local_pct']}% | Shimmer={res_stable['shimmer_local_pct']}%")
    print(f"   State: {res_stable['clinical_state']} (Strain Index: {res_stable['vocal_strain_index']}/100)")

    # 2. Vocal strain / tremor speech
    strained_frame = generate_voice_frame(freq=220.0, amp_mod=0.25)
    res_strained = analyzer.analyze_vocal_biomarkers(strained_frame)
    print()
    print(f"2. Strained Voice: F0={res_strained['fundamental_frequency_hz']} Hz | Jitter={res_strained['jitter_local_pct']}% | Shimmer={res_strained['shimmer_local_pct']}%")
    print(f"   State: {res_strained['clinical_state']} (Strain Index: {res_strained['vocal_strain_index']}/100)")

if __name__ == "__main__":
    main()
